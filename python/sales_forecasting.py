"""Export descriptive sales charts and forecast only when history permits."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from import_sales import ROOT, read_sales


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/raw-sales.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()
    sales = read_sales(args.input)
    frame = pd.DataFrame(sales)
    frame["date"] = pd.to_datetime(frame["date"])
    frame["total_amount"] = frame["total_amount"].astype(float)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    monthly = frame.set_index("date")["total_amount"].resample("MS").sum(min_count=1)
    monthly.to_csv(args.output_dir / "monthly_sales.csv", header=["revenue"])
    for name, series, title in [
        ("ventes_mensuelles", monthly.rename(index=lambda d: d.strftime("%Y-%m")), "Monthly revenue"),
        ("ventes_par_methode", frame.groupby("payment-method")["total_amount"].sum(), "Revenue by payment method"),
    ]:
        ax = series.plot.bar(figsize=(9, 5), rot=0)
        ax.set_title(title)
        ax.set_ylabel("Amount (currency unspecified)")
        plt.tight_layout()
        plt.savefig(args.output_dir / f"{name}.png")
        plt.close()
    forecast_path = args.output_dir / "forecast.csv"
    if len(monthly) < 12 or monthly.isna().any():
        forecast_path.unlink(missing_ok=True)
        print("Forecast unavailable: require at least 12 consecutive observed months. Confirm complete monthly coverage before forecasting.")
        return
    # Last three observed months form a temporal holdout for a simple baseline.
    train, actual = monthly.iloc[:-3], monthly.iloc[-3:]
    predictions = pd.Series(train.iloc[-1], index=actual.index)
    mae = (actual - predictions).abs().mean()
    future = pd.date_range(monthly.index[-1] + pd.offsets.MonthBegin(1), periods=6, freq="MS")
    pd.Series(monthly.iloc[-1], index=future, name="naive_forecast").to_csv(forecast_path)
    print(f"Last-value baseline holdout MAE={mae:.2f}. Six-month baseline exported; no seasonal model fitted.")


if __name__ == "__main__":
    main()
