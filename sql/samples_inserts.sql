-- Insert de ejemplo en fqre_assets
INSERT INTO fqre_assets (ticker, asset_name, asset_type, currency)
VALUES ('AAPL', 'Apple Inc.', 'STOCK', 'USD');

-- Insert de ejemplo en fqre_asset_prices
INSERT INTO fqre_asset_prices (
        asset_id, price_date, close_price, return_daily, vol_30d
)
VALUES (
        1,
        DATE '2024-11-01',
        180.50,
        0.0025,
        0.018
);
