from marshmallow import Schema, fields, INCLUDE, ValidationError

class StockDifferenceSchema(Schema):
    symbol = fields.Str(required=True, error_messages={"required": "symbol is required."})
    avg_purchase_cost = fields.Float(required=True, error_messages={"required": "avg_purchase_cost is required."})
    percent = fields.Float(required=True, error_messages={"required": "percent is required."})

class StockDetailsSchema(Schema):
    symbol = fields.Str(required=True, error_messages={"required": "symbol is required."})
    avg_purchase_cost = fields.Float(required=True, error_messages={"required": "avg_purchase_cost is required."})
    percent = fields.Float(required=True, error_messages={"required": "percent is required."})
    increase = fields.Boolean(required=True, error_messages={"required": "increase is required."})
    decrease = fields.Boolean(required=True, error_messages={"required": "decrease is required."})

class AddStocksSchema(Schema):
    stocks = fields.Nested(StockDetailsSchema, many=True, required=True, error_messages={"required": "stocks is required."})

