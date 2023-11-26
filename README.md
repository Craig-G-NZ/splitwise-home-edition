# splitwise-home-edition

This is a flask website used to help with managing expenses in our home. It will automatically calculate who owes who money and how much when splitting the cost 50/50 between two people.

It really only works for distributing money between 2 people as thats all I need. Don't expect anything like the real splitwise. Also "splitwise" is for namesake only, its not a replacement or a copy of the real splitwise app which is freaking awesome in its own right.

To use.....

  docker run -d \\ \
    --name splitwise-home-edition \\ \
    --restart always \\ \
    -p 80:80 \\ \
    -v /db_dir:/app/db:z \\ \
    -v /config_dir:/app/config:z \\ \
    -e TZ=Pacific/Auckland \\ \
    skippynz/splitwise-home-edition:latest

Create two directories: config and db

Inside the config directory, create a parameters.json file with the following code and replace name1 and name2 as required.
  
  {
      "names": ["name1", "name2"]
  }

An empty database will automatically be created in the db folder.

Feel free to create an issue if you want to discuss anything.
