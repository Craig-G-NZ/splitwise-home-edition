# splitwise-home-edition

This is a flask website used to help with managing expenses in our home. It will automatically calculate who owes who money and how much when splitting the cost 50/50 between two people.

It really only works for distributing money between 2 people as thats all I need. Don't expect anything like the real splitwise. Also "splitwise" is for namesake only, its not a replacement or a copy of the real splitwise app which is freaking awesome in its own right.

To use.....

  docker run -d \
    --name $CONTAINER_NAME \
    --restart always \
    --ip $IPADDRESS \
    -p $PORT:80 \
    -v $DB_DIR:/app/db:z \
    -v $CONFIG_DIR:/app/config:z \
    -e TZ=Pacific/Auckland \
    -e PUID=0 \
    -e GUID=0 \
    $IMAGE_NAME:latest

Create two directories:
  config
  db

Inside the config directory, create a parameters.json file with the following code and replace name1 and name2 as required.
  
  {
      "names": ["name1", "name2"]
  }

An empty database will automatically be created in the db folder.

Feel free to create an issue if you want to discuss anything.
