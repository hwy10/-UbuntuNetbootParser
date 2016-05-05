# coding=utf-8  
import configparser
import urllib.request
import socket
from bs4 import BeautifulSoup
import os
from mako.template import Template

def urlretrieve_report(count, block_size, total_size):
    print ("%0.2f%%" %(100.0 * count * block_size/ total_size), end='\r')
    
if __name__ == "__main__":

    # read config
    
    config = configparser.ConfigParser()
    config.read("ubuntu-netboot-parser.conf")
    conf = config["DEFAULT"]
    output_menu_path = conf.get("output_menu_path") or "linux.menu"
    image_base_url = conf.get("image_base_url") or "http://cdimage.ubuntu.com/netboot/"
    image_download_path = conf.get("image_download_path") or "linux_netboot_images"
    image_file_list = (conf.get("image_file_list") or "initrd.gz;linux;pxelinux.0").split(";")
    architecture = conf.get("default_architecture") or "amd64"
    menu_template_path = conf.get("menu_template_path") or "menu_template.txt"
    menu_file_path = conf.get("menu_file_path") or "linux.menu"
    
    # get netboot image list
    
    req = urllib.request.Request(image_base_url)
    html = urllib.request.urlopen(req)
    doc = html.read()
    
    # using BeautifulSoup to analyze
    
    soup = BeautifulSoup(doc)
    links = soup.find("ul").find_all("a")
    
    # download image files
    
    image_list = []
    for link in links:
        link_url = image_base_url + link['href']
        link_req = urllib.request.Request(link_url)
        link_html = urllib.request.urlopen(link_req)
        link_doc = link_html.read()
        link_soup = BeautifulSoup(link_doc)
        link_a = link_soup.find('a', text = architecture)

        dir_path = os.path.join(image_download_path, link.text)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        print(link.text)
        for file in image_file_list:
            file_url = link_a['href'] + "ubuntu-installer/" + architecture + "/" + file
            file_req = urllib.request.Request(file_url)
            file_path = os.path.join(image_download_path, link.text, file)
            print("Downloading %s:" % (file))
            if not os.path.exists(file_path):
                urllib.request.urlretrieve(file_url, file_path, reporthook=urlretrieve_report)
        image_list.append({'name': link.text, 'path': dir_path})    
    
    with open(menu_file_path, 'w') as menu_file:
        temp = Template(filename=menu_template_path)
        menu_file.write(temp.render(image_list = image_list))
        
        