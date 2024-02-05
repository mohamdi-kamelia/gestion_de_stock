import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

class StockManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion de Stock")
        
        # Connexion à la base de données 
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="kamelia",
            database="store"
        )
        self.cursor = self.db_connection.cursor()

        self.create_tables()
        
        self.create_widgets()

    def create_tables(self):
        # Vérifier si les catégories existent déjà
        self.cursor.execute("SELECT * FROM category")
        categories = self.cursor.fetchall()

        if not categories:
            self.cursor.execute("INSERT INTO category (name) VALUES ('Electronics')")
            self.cursor.execute("INSERT INTO category (name) VALUES ('Clothing')")

        # Vérifier si les produits existent déjà
        self.cursor.execute("SELECT * FROM product")
        products = self.cursor.fetchall()

        if not products:
            self.cursor.execute("INSERT INTO product (name, description, price, quantity, id_category) VALUES ('Laptop', 'Powerful laptop', 1000, 10, 1)")
            self.cursor.execute("INSERT INTO product (name, description, price, quantity, id_category) VALUES ('T-shirt', 'Cotton T-shirt', 20, 50, 2)")

        self.db_connection.commit()

    def create_widgets(self):
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Description", "Price", "Quantity", "Category"))
        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("ID", text="ID", anchor=tk.W)
        self.tree.heading("Name", text="Name", anchor=tk.W)
        self.tree.heading("Description", text="Description", anchor=tk.W)
        self.tree.heading("Price", text="Price", anchor=tk.W)
        self.tree.heading("Quantity", text="Quantity", anchor=tk.W)
        self.tree.heading("Category", text="Category", anchor=tk.W)
        self.tree.pack(expand=tk.YES, fill=tk.BOTH)

        button_bg_color = 'midnight blue'  
        button_fg_color = 'white' 

        refresh_button = tk.Button(self.root, text="Refresh", command=self.refresh_data, bg=button_bg_color, fg=button_fg_color)
        refresh_button.pack(pady=10)

        graph_button = tk.Button(self.root, text="Afficher le graphique", command=self.show_graph, bg=button_bg_color, fg=button_fg_color)
        graph_button.pack(pady=10)

        add_button = tk.Button(self.root, text="Ajouter Produit", command=self.add_product, bg=button_bg_color, fg=button_fg_color)
        add_button.pack(pady=10)

        delete_button = tk.Button(self.root, text="Supprimer Produit", command=self.delete_product, bg=button_bg_color, fg=button_fg_color)
        delete_button.pack(pady=10)

        update_button = tk.Button(self.root, text="Modifier Produit", command=self.update_product, bg=button_bg_color, fg=button_fg_color)
        update_button.pack(pady=10)

        export_button = tk.Button(self.root, text="Exporter en CSV", command=self.export_to_csv, bg=button_bg_color, fg=button_fg_color)
        export_button.pack(pady=10)

        # Charge les données au lancement du programme
        self.refresh_data()

    def refresh_data(self):
        # Efface les anciennes données du tableau
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Récupère les données de la base de données
        self.cursor.execute("SELECT * FROM product")
        products = self.cursor.fetchall()

        for product in products:
            self.tree.insert("", "end", values=product)

    def show_graph(self):
        try:
            self.cursor.execute("SELECT name, quantity FROM product")
            data = self.cursor.fetchall()

            product_names = [item[0] for item in data]
            quantities = [item[1] for item in data]

            plt.bar(product_names, quantities)
            plt.xlabel('Produits')
            plt.ylabel('Quantité en stock')
            plt.title('Stock de produits')
            plt.subplots_adjust(bottom=0.3) 
            plt.xticks(rotation=45, ha="right") 
            plt.show()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage du graphique : {str(e)}")

    def add_product(self):
  
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Ajouter un produit")

        tk.Label(self.add_window, text="Nom:").grid(row=0, column=0)
        self.name_entry = tk.Entry(self.add_window)
        self.name_entry.grid(row=0, column=1)

        tk.Label(self.add_window, text="Description:").grid(row=1, column=0)
        self.description_entry = tk.Entry(self.add_window)
        self.description_entry.grid(row=1, column=1)

        tk.Label(self.add_window, text="Prix:").grid(row=2, column=0)
        self.price_entry = tk.Entry(self.add_window)
        self.price_entry.grid(row=2, column=1)

        tk.Label(self.add_window, text="Quantité:").grid(row=3, column=0)
        self.quantity_entry = tk.Entry(self.add_window)
        self.quantity_entry.grid(row=3, column=1)

        tk.Label(self.add_window, text="Catégorie:").grid(row=4, column=0)
        self.category_entry = tk.Entry(self.add_window)
        self.category_entry.grid(row=4, column=1)

        def add_product_to_db():
            name = self.name_entry.get()
            description = self.description_entry.get()
            price = self.price_entry.get()
            quantity = self.quantity_entry.get()
            category_id = self.category_entry.get()

            try:
                self.cursor.execute("INSERT INTO product (name, description, price, quantity, id_category) VALUES (%s, %s, %s, %s, %s)",
                                    (name, description, price, quantity, category_id))
                self.db_connection.commit()

                self.refresh_data()

                self.add_window.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'ajout du produit : {str(e)}")

        tk.Button(self.add_window, text="Ajouter", command=add_product_to_db).grid(row=5, column=0, columnspan=2)

    def delete_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un produit à supprimer.")
            return

        product_id = self.tree.item(selected_item)['values'][0]

        try:
            self.cursor.execute("DELETE FROM product WHERE id = %s", (product_id,))
            self.db_connection.commit()

            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression du produit : {str(e)}")

    def update_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un produit à mettre à jour.")
            return

        product_id = self.tree.item(selected_item)['values'][0]

        update_window = tk.Toplevel(self.root)
        update_window.title("Mettre à jour le produit")

        self.cursor.execute("SELECT * FROM product WHERE id = %s", (product_id,))
        product_details = self.cursor.fetchone()

        tk.Label(update_window, text="Nom:").grid(row=0, column=0)
        name_entry = tk.Entry(update_window, textvariable=tk.StringVar(value=product_details[1]))
        name_entry.grid(row=0, column=1)

        tk.Label(update_window, text="Description:").grid(row=1, column=0)
        description_entry = tk.Entry(update_window, textvariable=tk.StringVar(value=product_details[2]))
        description_entry.grid(row=1, column=1)

        tk.Label(update_window, text="Prix:").grid(row=2, column=0)
        price_entry = tk.Entry(update_window, textvariable=tk.StringVar(value=product_details[3]))
        price_entry.grid(row=2, column=1)

        tk.Label(update_window, text="Quantité:").grid(row=3, column=0)
        quantity_entry = tk.Entry(update_window, textvariable=tk.StringVar(value=product_details[4]))
        quantity_entry.grid(row=3, column=1)

        tk.Label(update_window, text="Catégorie:").grid(row=4, column=0)
        category_entry = tk.Entry(update_window, textvariable=tk.StringVar(value=product_details[5]))
        category_entry.grid(row=4, column=1)

        def update_product_in_db():
            new_name = name_entry.get()
            new_description = description_entry.get()
            new_price = price_entry.get()
            new_quantity = quantity_entry.get()
            new_category_id = category_entry.get()

            try:
                self.cursor.execute("UPDATE product SET name=%s, description=%s, price=%s, quantity=%s, id_category=%s WHERE id=%s",
                                    (new_name, new_description, new_price, new_quantity, new_category_id, product_id))
                self.db_connection.commit()

                self.refresh_data()

                update_window.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la mise à jour du produit : {str(e)}")

        tk.Button(update_window, text="Mettre à jour", command=update_product_in_db).grid(row=5, column=0, columnspan=2)

    def export_to_csv(self):
        try:
       
            self.cursor.execute("SELECT * FROM product")
            products = self.cursor.fetchall()

            csv_file_path = "products_in_stock.csv"

            with open(csv_file_path, mode='w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                
              
                csv_writer.writerow(["ID", "Nom", "Description", "Prix", "Quantité", "Catégorie"])
                for product in products:
                    csv_writer.writerow(product)

            
            messagebox.showinfo("Export réussi", f"Les produits ont été exportés en CSV : {csv_file_path}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'exportation en CSV : {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockManagementApp(root)
    root.mainloop()
