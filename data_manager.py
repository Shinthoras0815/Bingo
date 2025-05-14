# data_manager.py

import random
import json
from tkinter import messagebox

class DataManager:
    def __init__(self):
        self.lists = {}

    def save_to_file(self, file_path):
        # save the current state of the lists to a file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.lists, f, ensure_ascii=False, indent=2)

    def load_from_file(self, file_path):
        # load the lists from a file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.lists = data
                return True
        except FileNotFoundError:
            return False



    def add_category(self,name, weight):
        # add new category to the game
        self.lists[name] = {'words': [], 'weight': weight ,'used': False}

    def remove_category(self, name):
        # remove category from the game
        if name in self.lists:
            del self.lists[name]

    def add_word(self, category, word):
        # add new words to the category
        if category in self.lists:
            self.lists[category]['words'].append(word)

    def remove_word(self, category, word):
        # remove word from the category
        if category in self.lists and word in self.lists[category]['words']:
            self.lists[category]['words'].remove(word)

    def set_weight(self,category,weight):
        # set the weight of the category
        if category in self.lists:
            self.lists[category]['weight'] = weight

    def weighted_pool(self):
        # create a weighted pool of words based on their weights
        pool = []
        for cat, info in self.lists.items():
            if info['used']:
                pool.extend(info['words'] * info['weight'])
        return pool

    def draw_unique(self,size = 25):
        #draw unique words from the weighted pool
        pool = self.weighted_pool()
        max_unique = min(size, len(set(pool))) # number of unique words
        drawn = []

        while len(drawn) < max_unique and pool:
            choice = random.choice(pool)
            drawn.append(choice)
            # remove all occurrences of choice
            pool = [w for w in pool if w != choice]

        return drawn




