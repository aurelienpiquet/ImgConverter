import os

from PIL import Image

class CustomImage:
    def __init__(self, path, folder = "reduced"):
        self.image = Image.open(path)
        self.width, self.height = self.image.size
        self.path = path
        self.reduced_path = os.path.join(os.path.dirname(self.path), folder, os.path.basename(self.path))
        #Créer le path du fichier "C:\Users\AP\PycharmProjects\pythonProject\formation_udemy\PyConverter\customUi\reduced\Lighthouse.jpg"

    def __repr__(self):
        return "{}".format(self.path)

    def reduce_image(self, new_size=0.5, new_quality=75):
        new_width = round(self.width * new_size)
        new_height = round(self.height * new_size)
        self.image = self.image.resize((new_width, new_height), Image.ANTIALIAS) # ANTIALIAS evite la perte de qualité lors d'un chagnement de size
        parent_dir = os.path.dirname(self.reduced_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        self.image.save(self.reduced_path, 'JPEG', quality=new_quality)
        return os.path.exists(self.reduced_path) #renvoi true si image est dans le dossier reduced, false si pas dans le dossier
        

if __name__ == "__main__":
    i = CustomImage(r"C:\Users\AP\PycharmProjects\pythonProject\formation_udemy\PyConverter\customUi\test_images\s01_t01_pc.jpg")
    i.reduce_image(1,10)
    
   