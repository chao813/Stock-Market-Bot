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

class TrackedStocksSchema(Schema):
    symbol = fields.Str()
    detailed = fields.Boolean(required=True, error_messages={"required": "decrease is required."})

class TrackedStocksNews(Schema):
    symbol = fields.Str()
    start = fields.Date(required=True, error_messages={"required": "Start date is required."})
    end = fields.Date(required=True, error_messages={"required": "End date is required."})
    detailed = fields.Boolean(required=True, error_messages={"required": "decrease is required."})
