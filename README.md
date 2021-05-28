# CooperativeUAVFireFighting
Project for AASMA course (UAV firefighting simulation)

For this project we have using python version 3.8.

In order to run this simulator make sure the **main.py** executable is
in the src folder;  
Next, make sure to have installed the pygame library as it is necessary for the simulation;
Lastly, run the command `python3 main.py` which will promp a new windowed screen.

Alternatively, opening the project in an IDE, such as PyCharm, and running the **main.py**  
script from the IDE will also prompt the new windowed screen.

After each simulation, it is needed to relaunch the script as it does not have a reset feauture.

In the windowed pygame screen you will have **4** main buttons:
One to change step by step mode  from **true/false** and three buttons for each of the approaches
to be employed in the simulation.

Pressing one of the approach buttons will begin the simulation which will run on its own until the  
end conditions are verified (or in case of step = True it will only simulate next step one button  
with said name is pressed).

There is an indication below the buttons on the left of the Wind Direction for that simulation  
which is not a button and will be randomly selected every simulation.

The video demonstration will include all the steps for a successful simulation.
