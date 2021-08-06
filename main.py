import yaml


class recipe:
    def __init__(self, docName):
        doc = open(docName, 'r')
        temp = yaml.load(doc,Loader=yaml.FullLoader)
        self.sortedDict = sorted(temp, key=lambda item: temp[item]['priority'],reverse=True)
        self.recipes = temp

class food:
    def __init__(self, docName):
        doc = open(docName, 'r')
        self.foods = yaml.load(doc, Loader=yaml.FullLoader)

    def getFood(self, foodName):
        if foodName in self.foods: return self.foods[foodName]
        # cooked food
        if foodName.endswith("_cooked"):
            temp = self.foods[foodName[:-7]]
            if ("derivative" not in temp) or ('cooked' not in temp['derivative']): raise ErrFoodNotExist(foodName)
            temp['tags']['precook'] = 1
            return temp
        # dried food
        if foodName.endswith("_dried"):
            temp = self.foods[foodName[:-6]]
            if ("derivative" not in temp) or ('dried' not in temp['derivative']): raise ErrFoodNotExist(foodName)
            temp['tags']['dried'] = 1
            return temp


class cookpot:
    def __init__(self, recipeClass, foodClass):
        self.recipes = recipeClass.recipes
        self.foods = foodClass.foods


class ingredients:
    def __init__(self, foodClass, foods=None):
        self.foodList = [] if foods is None else foods
        self.foodClass = foodClass
        self.calcTags()

    def calcTags(self):
        self.tags = {}
        for food in self.foodList:
            foodObject = self.foodClass.getFood(food)
            for tag in foodObject['tags']:
                self.tags[tag] = self.tags.setdefault(tag, 0) + foodObject['tags'][tag]

    def getNames(self):
        return self.foodList

    def getTags(self):
        return self.tags

    def addFood(self, foodName):
        if len(self.foodList) == 4: raise ErrIngredientsNumber
        foodObject = self.foodClass.getFood(foodName)
        for tag in foodObject['tags']:
            self.tags[tag] = self.tags.setdefault(tag, 0) + foodObject['tags'][tag]

    def removeFood(self, foodName):
        if len(self.foodList) == 0: raise ErrIngredientsNumber
        foodObject = self.foodClass.getFood(foodName)
        for tag in foodObject['tags']:
            self.tags[tag] -= foodObject['tags'][tag]

    def getRecipe(self, recipeClass):
        pass

    def getOnlyRecipe(self, recipeClass):  # used when the cookpot is full, thus only one dish is able to be made
        for rName in recipeClass.sortedDict:
            recipe = recipeClass.recipes[rName]
            dishFailed = False
            for tag in self.tags:
                # first check if the dish explicitly excludes a tag
                if ('exclude' in recipe['requirement']) and (tag in recipe['requirement']['exclude']):
                    dishFailed = True
                    break
            if dishFailed: continue
            #check if the Tag is within the range of the recipe
            if 'needTag' in recipe['requirement']:
                for tag, tagMin in recipe['requirement']['needTag'].items():
                    if (tag not in self.tags) or self.tags[tag] < tagMin :
                        dishFailed = True
                        break
            if dishFailed: continue
            if 'max' in recipe['requirement']:
                for tag, tagMax in recipe['requirement']['max'].items():
                    if (tag in self.tags) and self.tags[tag] >tagMax:
                        dishFailed = True
                        break
            if dishFailed: continue
            #check if all the food name is satisfied
            if 'needName' in recipe['requirement']:
                tempIng = self.foodList.copy()
                for need in recipe['requirement']['needName']: #Needs a good algorithm here
                    hasFood = False
                    for i in range(len(tempIng)):
                        if tempIng[i] in need:
                            hasFood = True
                            tempIng.pop(i)
                            break
                    if not hasFood:
                        dishFailed = True
                        break
            if dishFailed: continue
            return rName


    def getPossibleRecipe(self, recipeClass):  # list all the possible recipes that could be made
        pass


class ErrFoodNotExist(Exception):
    def __init__(self, foodName):
        self.foodName = foodName
        self.message = "does not exist in the food list"

    def __str__(self):
        return f'{self.foodName} {self.message}'


class ErrIngredientsNumber(Exception):
    pass


if __name__ == "__main__":
    classicFood = food("foods.yml")
    classicRecipe = recipe("recipes.yml")
    myIng = ingredients(classicFood,['butter','berries','egg','ice'])
    print(myIng.getOnlyRecipe(classicRecipe))