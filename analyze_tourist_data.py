# analyze_tourist_data.py

import tkinter as tk
from tkinter import ttk
import json
import generate_tourist_data

def load_data_from_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)
    
class TreeNode:
    def __init__(self, name, data=None):
        self.name = name
        self.data = data
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def serialize(self):
        return {
            "name": self.name,
            "children": [child.serialize() for child in self.children]
        }

class LocationNode(TreeNode):
    def __init__(self, name):
        super().__init__(name)
        self.types = {}

    def add_type(self, type_name):
        if type_name not in self.types:
            new_type_node = TypeNode(type_name)
            self.types[type_name] = new_type_node
            self.add_child(new_type_node)
        return self.types[type_name]

    def serialize(self):
        data = super().serialize()
        data["types"] = {k: v.serialize() for k, v in self.types.items()}
        return data

class TypeNode(TreeNode):
    def __init__(self, name):
        super().__init__(name)
        self.ratings = {}

    def add_rating(self, rating):
        if rating not in self.ratings:
            new_rating_node = RatingNode(rating)
            self.ratings[rating] = new_rating_node
            self.add_child(new_rating_node)
        return self.ratings[rating]

    def serialize(self):
        data = super().serialize()
        data["ratings"] = {k: v.serialize() for k, v in self.ratings.items()}
        return data

class RatingNode(TreeNode):
    def __init__(self, name):
        super().__init__(name)
        self.reviews = {}

    def add_review(self, review_count):
        if review_count not in self.reviews:
            new_review_node = ReviewNode(review_count)
            self.reviews[review_count] = new_review_node
            self.add_child(new_review_node)
        return self.reviews[review_count]

    def serialize(self):
        data = super().serialize()
        data["reviews"] = {k: v.serialize() for k, v in self.reviews.items()}
        return data

class ReviewNode(TreeNode):
    def __init__(self, name):
        super().__init__(name)

    def serialize(self):
        return super().serialize()
    

def build_tree(places_data):
    root = LocationNode("Locations")

    for location, places in places_data.items():
        location_node = LocationNode(location)
        root.add_child(location_node)  # 这里添加子节点

        for place in places:
            for place_type in place.get('types', []):
                type_node = location_node.add_type(place_type)  # 确保这里返回有效的节点

                rating = str(place.get('rating', 'N/A'))
                rating_node = type_node.add_rating(rating)  # 确保这里返回有效的节点

                reviews = str(place.get('user_ratings_total', 'N/A'))
                review_node = rating_node.add_review(reviews)  # 确保这里返回有效的节点

                place_node = TreeNode(place['name'], data=place)
                review_node.add_child(place_node)  # 正确添加子节点

    return root



def recommend_places(root, location_query, type_query=None, min_rating=None, min_reviews=None):
    recommendations = []

    for location_node in root.children:
        if location_query.lower() in location_node.name.lower():
            for type_node in location_node.children:
                if type_query and type_query.lower() in type_node.name.lower():
                    for rating_node in type_node.children:
                        rating = float(rating_node.name) if rating_node.name != 'N/A' else 0
                        if min_rating is None or rating >= min_rating:
                            for review_node in rating_node.children:
                                reviews = int(review_node.name) if review_node.name != 'N/A' else 0
                                if min_reviews is None or reviews >= min_reviews:
                                    for place_node in review_node.children:
                                        recommendations.append(place_node.data)
    return recommendations



def create_gui(api_key):
    # 全局变量，用于在步骤之间传递信息
    selected_city = None
    selected_type = None
    min_rating = None
    min_reviews = None

    def on_city_confirm():
        nonlocal selected_city
        selected_city = city_entry.get()
        update_step_2()

    def on_type_confirm():
        nonlocal selected_type
        selected_type = type_combobox.get()
        update_step_3()

    def on_rating_confirm():
        nonlocal min_rating
        min_rating = float(rating_entry.get()) if rating_entry.get() else 0
        update_step_4()

    def on_review_confirm():
        nonlocal min_reviews
        min_reviews = int(reviews_entry.get()) if reviews_entry.get() else 0
        fetch_and_display_recommendations()

    def fetch_and_display_recommendations():
        # 加载JSON文件数据
        places_data = load_data_from_json("tourist_data_set.json")
        # 构建树结构
        root = build_tree(places_data)
        recommendations = recommend_places(root, selected_city, selected_type, min_rating, min_reviews)
        display_recommendations(recommendations)

    def update_step_2():
    # 显示类型选择相关的控件
        type_label.pack(padx=10, pady=5)
        type_combobox.pack(padx=10, pady=5)
        type_confirm_button.pack(padx=10, pady=5)

    # 隐藏城市选择相关的控件
        city_entry.pack_forget()
        city_confirm_button.pack_forget()

    def update_step_3():
    # 显示评分输入相关的控件
        rating_label.pack(padx=10, pady=5)
        rating_entry.pack(padx=10, pady=5)
        rating_confirm_button.pack(padx=10, pady=5)

    # 隐藏类型选择相关的控件
        type_combobox.pack_forget()
        type_confirm_button.pack_forget()

    def update_step_4():
    # 显示评价人数输入相关的控件
        reviews_label.pack(padx=10, pady=5)
        reviews_entry.pack(padx=10, pady=5)
        reviews_confirm_button.pack(padx=10, pady=5)

    # 隐藏评分输入相关的控件
        rating_entry.pack_forget()
        rating_confirm_button.pack_forget()

    def display_recommendations(recommendations):
        recommendations_text.delete("1.0", tk.END)
        if not recommendations:
            recommendations_text.insert(tk.END, "No available recommendations based on the filters.\n")
        else:
            for place in recommendations:
                formatted_info = (
                    f"Name: {place['name']}\n"
                    f"Rating: {place.get('rating', 'N/A')}\n"
                    f"Number of Reviews: {place.get('user_ratings_total', 'N/A')}\n"
                    f"Address: {place.get('formatted_address', 'N/A')}\n\n"
                )
                recommendations_text.insert(tk.END, formatted_info)
       

    root = tk.Tk()
    root.title("Travel Destination Recommender")

    # 第一步：城市输入
    ttk.Label(root, text="Enter a city:").pack(padx=10, pady=5)
    city_entry = ttk.Entry(root)
    city_entry.pack(padx=10, pady=5)
    city_confirm_button = ttk.Button(root, text="Confirm City", command=on_city_confirm)
    city_confirm_button.pack(padx=10, pady=5)

    # 第二步：类型选择（初始时隐藏）
    type_label = ttk.Label(root, text="Select a type:")
    type_combobox = ttk.Combobox(root)
    type_confirm_button = ttk.Button(root, text="Confirm Type", command=on_type_confirm)

    # 第三步：评分输入（初始时隐藏）
    rating_label = ttk.Label(root, text="Minimum rating:")
    rating_entry = ttk.Entry(root)
    rating_confirm_button = ttk.Button(root, text="Confirm Rating", command=on_rating_confirm)

    # 第四步：评价人数输入（初始时隐藏）
    reviews_label = ttk.Label(root, text="Minimum number of reviews:")
    reviews_entry = ttk.Entry(root)
    reviews_confirm_button = ttk.Button(root, text="Confirm Reviews", command=on_review_confirm)

    recommendations_text = tk.Text(root, height=15, width=50)

    recommendations_text.pack(padx=10, pady=10)

    root.mainloop()



def main():
    api_key = 'AIzaSyBlP0PfB6LGsrgS4urCdE9Mn22fwfaJSFw'

    create_gui(api_key)


if __name__ == "__main__":
    main()
