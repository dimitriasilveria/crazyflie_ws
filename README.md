# Crazyflies workspace 

## The first thing to do is to select the crazyflies you intend to fly in the configuration file:
1. Go to the file [crazyflie.yaml](crazyswarm2/crazyflie/config/crazyflies.yaml) 
2. Under the drone's name, set the flag "enable"
3. Open a terminal, go to the src folder of your workspace:

    ```cd ~/ros2_ws/src```

3. Run the command, to build the crazyflie package : 

    ```colcon build --packages-select crazyflie```

## Running all the launch files and nodes
* If you haven't add the source commands to your .bash.rc, don't forget to run 
```source /opt/ros/humble/setup.bash && source ~/ros2_ws/install/local_setup.bash``` in all the terminal that you use for the steps in this section

1- Open a terminal and run the command ```source ~/crazyflies_env/bin/activate``` to activate the virtual environment.
  
2- On the previous terminal, run the [encirclement_launch.py](crazy_encirclement/launch/encirclement_launch.py) file:

``` ros2 launch crazy_encirclement encirclement_launch.py```

* This launch runs the motion capture, the watch dog, the crazy server and the agents order node. 

3 - For safety, first open a terminal and run the node that sends a landing command to all the drones:
```ros2 run controller_pkg landing``

* To send the landing command, click on the terminal where this node is runnig and press ```Enter``` 

4- Now, the nodes that send the commands to the drones has to be run. For that, open one terminal for each drone you want to fly, and run: 

``` ros2 run crazy_encirclement circle_distortion --ros-args -p robot:="C05" --remap __node:=distortion_05```

* The argument "robot" must the the name of the robot you want to fly, and you also must substitute "distortion_05" for "distortion" + <number of drone>.

5- After running one node for each drone, they will NOT take off. You have to click on the terminal where each node is running and press ```Enter```

6- After all of them take off, in another terminal, run the the node that sends the drone a flag to start the trajectory:

```ros2 run controller_pkg encircling```
* Click on the terminal where this node is running and press ```Enter``` to start the encirclement.

**If anything goes wrong, click on the terminal where the landing node is running and press enter.**

