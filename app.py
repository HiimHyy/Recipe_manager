import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import psycopg2

class RecipeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recipe Management System")

        # Connect to the database
        self.conn = psycopg2.connect(
            dbname="recipe",
            user="postgres",
            host="localhost"
        )
        self.cur = self.conn.cursor()

        # Create the GUI
        self.create_widgets()

        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

    def create_widgets(self):
        # Create a frame for the navigation bar
        self.navbar = tk.Frame(self.root)
        self.navbar.grid(sticky="nsew")

        for i in range(6):
            self.navbar.columnconfigure(i, weight=1)

        # Place the search entry and button in the navigation bar
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.navbar, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # Use grid instead of pack

        # Place the buttons in the navigation bar
        self.search_button = tk.Button(self.navbar, text="Search", command=self.search_recipes)
        self.search_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")  # Use grid instead of pack

        self.refresh_button = tk.Button(self.navbar, text="Refresh", command=self.refresh_recipes)
        self.refresh_button.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")  # Use grid instead of pack

        self.add_button = tk.Button(self.navbar, text="Add Recipe", command=self.add_recipe)
        self.add_button.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")  # Use grid instead of pack

        self.delete_button = tk.Button(self.navbar, text="Delete Recipe", command=self.delete_recipe)
        self.delete_button.grid(row=0, column=4, padx=10, pady=10, sticky="nsew")  # Use grid instead of pack

        # Place the update button in the navigation bar
        self.update_button = tk.Button(self.navbar, text="Update Recipe", command=self.update_recipe)
        self.update_button.grid(row=0, column=5, padx=10, pady=10, sticky="nsew")

        self.recipe_listbox = tk.Listbox(self.root, width=50)
        self.recipe_listbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.recipe_listbox.bind('<<ListboxSelect>>', self.show_recipe_details)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.refresh_recipes()

    def search_recipes(self):
        pass

    def refresh_recipes(self):
        # Clear the listbox
        self.recipe_listbox.delete(0, tk.END)

        # Fetch recipes from the database
        self.cur.execute("SELECT title FROM recipes")
        recipes = self.cur.fetchall()
        for recipe in recipes:
            self.recipe_listbox.insert(tk.END, recipe[0])

    def add_recipe(self):
       title = simpledialog.askstring("Input", "What is the recipe name?")
       cooking_time = simpledialog.askstring("Input", "What is the cooking time?")
       ingredients_input = simpledialog.askstring("Input", "What are the ingredients?")
       instructions = simpledialog.askstring("Input", "What are the instructions?")
       cooking_hardware = simpledialog.askstring("Input", "What are the cooking hardwares?")

       # Check if the user has entered all the details
       if title and cooking_time and ingredients_input and instructions and cooking_hardware:
           # Insert the new recipe into the recipes table
           self.cur.execute("INSERT INTO recipes (title, cooking_time, instructions, cooking_hardware) VALUES (%s, %s, %s, %s) RETURNING id",
                            (title, cooking_time, instructions, cooking_hardware))
           recipe_id = self.cur.fetchone()[0]  # Get the ID of the inserted recipe
           
           # Split ingredients string and insert into ingredients table
           for ingredient in ingredients_input.split(","):
               ingredient = ingredient.strip()  # Remove leading/trailing whitespace
               
               # Check if the ingredient already exists in the ingredients table
               self.cur.execute("SELECT id FROM ingredients WHERE name = %s", (ingredient,))
               existing_ingredient = self.cur.fetchone()
               
               if not existing_ingredient:
                   # Insert the ingredient into the ingredients table
                   self.cur.execute("INSERT INTO ingredients (name, recipe_id) VALUES (%s, %s)", (ingredient, recipe_id))
           
           self.conn.commit()

           # Refresh the list of recipes
           self.refresh_recipes()
       else:
           messagebox.showerror("Error", "You must enter all the details for the recipe")

    def show_recipe_details(self, event):
        # Get the selected recipe name
        selected_recipe = self.recipe_listbox.get(self.recipe_listbox.curselection())

        # Fetch the details of the selected recipe from the database
        self.cur.execute("SELECT title, cooking_time, ingredients, instructions, cooking_hardware FROM recipes WHERE title = %s", (selected_recipe,))
        recipe_details = self.cur.fetchone()

        messagebox.showinfo("Recipe Details", f"Title: {recipe_details[0]}\nCooking Time: {recipe_details[1]}\nIngredients: {recipe_details[2]}\nInstructions: {recipe_details[3]}\nCooking Hardware: {recipe_details[4]}")

    def delete_recipe(self):
        # Get the selected recipe name
        selected_recipe = self.recipe_listbox.get(self.recipe_listbox.curselection())

        # Confirm the deletion with the user
        confirmation = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the recipe '{selected_recipe}'?")

        if confirmation:
            # Delete the recipe from the database
            self.cur.execute("DELETE FROM recipes WHERE title = %s", (selected_recipe,))
            self.conn.commit()

            # Refresh the list of recipes
            self.refresh_recipes()

    def update_recipe(self):
        # Create a new window for updating the recipe
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Recipe")

        # Create labels and entry fields for the recipe details
        title_label = tk.Label(update_window, text="Recipe Name:")
        title_label.grid(row=0, column=0, padx=10, pady=10)
        title_entry = tk.Entry(update_window)
        title_entry.grid(row=0, column=1, padx=10, pady=10)

        cooking_time_label = tk.Label(update_window, text="Cooking Time:")
        cooking_time_label.grid(row=1, column=0, padx=10, pady=10)
        cooking_time_entry = tk.Entry(update_window)
        cooking_time_entry.grid(row=1, column=1, padx=10, pady=10)

        ingredients_label = tk.Label(update_window, text="Ingredients:")
        ingredients_label.grid(row=2, column=0, padx=10, pady=10)
        ingredients_entry = tk.Entry(update_window)
        ingredients_entry.grid(row=2, column=1, padx=10, pady=10)

        instructions_label = tk.Label(update_window, text="Instructions:")
        instructions_label.grid(row=3, column=0, padx=10, pady=10)
        instructions_entry = tk.Entry(update_window)
        instructions_entry.grid(row=3, column=1, padx=10, pady=10)

        cooking_hardware_label = tk.Label(update_window, text="Cooking Hardware:")
        cooking_hardware_label.grid(row=4, column=0, padx=10, pady=10)
        cooking_hardware_entry = tk.Entry(update_window)
        cooking_hardware_entry.grid(row=4, column=1, padx=10, pady=10)

        # Get the selected recipe name
        selected_recipe = self.recipe_listbox.get(self.recipe_listbox.curselection())

        # Fetch the details of the selected recipe from the database
        self.cur.execute("SELECT title, cooking_time, ingredients, instructions, cooking_hardware FROM recipes WHERE title = %s", (selected_recipe,))
        recipe_details = self.cur.fetchone()

        # Set the initial values of the entry fields to the current recipe details
        title_entry.insert(tk.END, recipe_details[0])
        cooking_time_entry.insert(tk.END, recipe_details[1])
        if recipe_details[2] is not None and isinstance(recipe_details[2], str):
            ingredients_entry.insert(tk.END, recipe_details[2])
        instructions_entry.insert(tk.END, recipe_details[3])
        cooking_hardware_entry.insert(tk.END, recipe_details[4])

        def update_recipe_details():
            # Get the updated recipe details from the entry fields
            updated_title = title_entry.get()
            updated_cooking_time = cooking_time_entry.get()
            updated_ingredients = ingredients_entry.get()
            updated_instructions = instructions_entry.get()
            updated_cooking_hardware = cooking_hardware_entry.get()

            # Update the recipe in the database
            self.cur.execute("UPDATE recipes SET title = %s, cooking_time = %s, ingredients = %s, instructions = %s, cooking_hardware = %s WHERE title = %s",
                             (updated_title, updated_cooking_time, updated_ingredients, updated_instructions, updated_cooking_hardware, selected_recipe))
            self.conn.commit()


            self.cur.execute("SELECT id FROM recipes WHERE title = %s", (updated_title,))
            recipe_id = self.cur.fetchone()[0]

            # Split updated ingredients string and update ingredients table
            for ingredient in updated_ingredients.split(","):
                ingredient = ingredient.strip()  # Remove leading/trailing whitespace

            # Check if the ingredient already exists in the ingredients table
            self.cur.execute("SELECT id FROM ingredients WHERE name = %s AND recipe_id = %s", (ingredient, recipe_id))
            existing_ingredient = self.cur.fetchone()

            if not existing_ingredient:
                # Insert the ingredient into the ingredients table
                self.cur.execute("INSERT INTO ingredients (name, recipe_id) VALUES (%s, %s)", (ingredient, recipe_id))
            else:
                # Update the ingredient in the ingredients table
                self.cur.execute("UPDATE ingredients SET name = %s WHERE id = %s", (ingredient, existing_ingredient[0]))

            self.conn.commit()

            # Refresh the list of recipes
            self.refresh_recipes()

            # Close the update window
            update_window.destroy()

        # Create the update button
        update_button = tk.Button(update_window, text="Update", command=update_recipe_details)
        update_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def on_close(self):
        # Close the database connection
        self.cur.close()
        self.conn.close()

        # Close the application
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeApp(root)
    root.mainloop()
