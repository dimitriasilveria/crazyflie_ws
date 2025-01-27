# Crazyflies workspace 

## The first thing to do is to select the crazyflies you intend to fly in the configuration file:
    1. Go to the file [crazyflie.yaml](crazyswarm2/crazyflie/config/crazyflies.yaml) 
    2. Under the drone's name, set the flag "enable"
    3. Open a terminal, go to the src folder of your workspace:
    ```cd ~/ros2_ws/src```
    3. Run the command, to build the crazyflie package : 
    ```colcon build --packages-select crazyflie```
