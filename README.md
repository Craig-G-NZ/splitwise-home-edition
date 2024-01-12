# splitwise-home-edition

This is a flask website used to help with managing expenses in our home. It will automatically calculate who owes who money and how much when splitting the cost 50/50 between two people.

It really only works for distributing money between 2 people as thats all I need. Don't expect anything like the real splitwise. Also "splitwise" is for namesake only, its not a replacement or a copy of the real splitwise app which is freaking awesome in its own right.

To use.....

    docker run -d \
      --name splitwise-home-edition \
      --restart always \
      -p 80:80 \
      -v /data_dir:/app/data:z \
      -e TZ=Pacific/Auckland \
      skippynz/splitwise-home-edition:latest

Create a directory and name it whatever you want e.g. data_dir - this will be used above in your docker command for the volume (-v). An empty database will be automatically created in the "data_dir" folder. You will need to create a "config.json" file in the data_dir folder with the following content. Change as you see fit. If you dont create the file you wont be able to select the names of the people you want to split between and it might self name to "Default Title" and "Default Name".
  
    {
        "names": ["name1", "name2"],
        "website_title": "Money Tracker",
        "website_name": "Money Tracker"
    }

Feel free to create an issue if you want to discuss anything.

![image](https://github.com/Craig-G-NZ/splitwise-home-edition/assets/92700720/1293c8aa-b1d8-4790-8510-783acbd4fcb7)
![image](https://github.com/Craig-G-NZ/splitwise-home-edition/assets/92700720/e4469bb8-604a-494d-966a-887eb03d091f)
