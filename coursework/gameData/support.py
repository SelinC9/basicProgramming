import pygame
from os import walk #walk through different folders
import os

print("Current working directory:", os.getcwd())


def importFolder(path): #import all the images from a folder
    surface_list = [] #list of surfaces

    for _, _, image_files in walk(path): #walk through the folder
        for image in sorted(image_files): #for each image in the folder
            if image.lower().endswith(('.png', '.jpg', '.jpeg')): #check if the image is a png or jpg
                fullPath = path + "/"  +image
                print('Loading:', fullPath) #testing purposes
                imageSurf = pygame.image.load(fullPath).convert_alpha() #load the image and convert it to a surface
                surface_list.append(imageSurf) #append the image to the list

    return surface_list #return the list of surfaces