class Owner:
    def __init__(self, name, available_minutes, preferences, pets):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences
        self.pets = pets

    def add_pet(self, pet):
        pass

    def get_owner_info(self):
        pass


class Pet:
    def __init__(self, name, species, breed, age, tasks):
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.tasks = tasks

    def get_pet_info(self):
        pass


class Task:
    def __init__(self, title, duration_minutes, priority, category, completed):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.completed = completed

    def edit(self, title, duration_minutes, priority):
        pass


class Scheduler:
    def __init__(self, owner, pet, tasks):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def enter_task(self, task):
        pass

    def edit_task(self, task_index, title, duration_minutes, priority):
        pass

    def generate_plan(self):
        pass

    def explain_plan(self):
        pass
