from graphene import InputObjectType, ID, Float, String, Int, Boolean


class StringComparator(InputObjectType):
    eq = ID(description="Equal operator")
    like = ID(name="like", description="Like operator")


class IntComparator(InputObjectType):
    eq = ID(description="Equal operator")
    lte = ID(description="Lower than or equal to operator")
    lt = ID(description="Lower then operator")
    gte = ID(description="Greater than or equal to operator")
    gt = ID(description="Greater then operator")


class FloatComparator(InputObjectType):
    eq = Float(description="Equal operator")
    lte = Float(description="Lower than or equal to operator")
    lt = Float(description="Lower then operator")
    gte = Float(description="Greater than or equal to operator")
    gt = Float(description="Greater then operator")


class BooleanComparator(InputObjectType):
    eq = Boolean(description="Equal operator for boolean", namme="is")


class InputType(InputObjectType):
    operator = String()
    limit = Int()
