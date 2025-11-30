CREATE OR REPLACE VIEW v_asset_volatility AS
SELECT
    a.asset_id,
    a.ticker,
    p.price_date,
    p.close_price,
    p.return_daily,
    p.vol_30d
FROM fqre_assets a
JOIN fqre_asset_prices p
    ON a.asset_id = p.asset_id;
