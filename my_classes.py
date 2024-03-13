# object for an api endpoint
class Endpoint():
    def __init__(self, name) -> None:
        self.name = name
    # contruct the endpoint url

    # test it

    # print the url
    def __str__(self) -> str:
        return f"{self.name}"

# an object to represent a call to one of the endpoints
class apiCall():
    # contruct the url string
    def __init__(self, endpoint):
        if endpoint == 'an endpoint':
            endpoint
            url = endpoint
    # return the url for the apiCall
    def __str__():
        pass
    # return the response
    def get_reponse():
        pass

    #  

# class for ingredients
class Ingredient():
    # ingredients always have a name and an amount
    def __init__(self, name, amount):
        self.r = name
        self.i = amount
    
    # returned when printing class instance
    def __str__(self):
        return f"{self.name}({self.amount})"


# class for equipment

# class for instructions

# class for recipe - inherits other classes, no

# equipment, instructions, ingredients are components of a recipe