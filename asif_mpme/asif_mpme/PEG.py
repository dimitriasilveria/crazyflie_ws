import numpy as np

class Evader:
    def __init__(self, pos, status):
        self.position = pos
        self.status = status

    def __str__(self):
        """
        String representation of the agent, showing its location and status.
        """
        return f"Evader Location: {self.position}"
    
    def update_position(self, pos):
        self.position = pos


class Pursuer:
    def __init__(self, pos, dynamics):
        self.position = pos
        self.dynamics = dynamics
        self.status = 0

    def __str__(self):
        """
        String representation of the agent, showing its location and status.
        """
        return f"Pursuer Location: {self.position}"
    
    def update_position(self, pos):
        self.position = pos



class PEGCore:

    def __init__(self):
        # Lifecycle
        self.initialized = False

        # Entities
        self.pursuers = []
        self.evaders = []

        # Evader activation
        self.activation_time = {}

        # Task assignment
        self.lambda_rate = 30
        self.assignment = None

        # Variables
        self.target = [0, 0]
        self.evader_wins = False
        self.pursuer_wins = False

        # Time
        self.time = 0
        self.agent_velocity = 5
        self.dt = 0.02

    def game_init(self, pursuer_positions, evader_positions, target=[0, 0]):

        self.pursuers = []
        self.evaders = []
        # print(f"Pursuer Positions: {[[f'{v:.3f}' for v in p] for p in pursuer_positions]}")

        # Create pursuers
        for pos in pursuer_positions:
            self.pursuers.append(Pursuer(pos, dynamics=1))

        # Create evaders
        for pos in evader_positions:
            status = np.random.choice([0, 1])
            self.evaders.append(Evader(pos, status=status))

        # Global state
        self.activation_time = self._create_activation_timestamps()
        self.assignment = task_assignment() if self.assignment is None else self.assignment
        self.target = target

        self.time = 0
        self.pursuer_wins = False
        self.evader_wins = False

        self.initialized = True

        return None #self._get_observation()   # optional but recommended

    

    # --------------------------------------------------
    # Main step (called by function wrapper)
    # --------------------------------------------------
    def step(self, pursuer_positions, evader_positions, target= [0,0]):

        # ==================================================
        # STEP 0 — ONE-TIME INITIALIZATION
        # ==================================================
        if not self.initialized:
            raise RuntimeError("Environment not initialized. Call game_init() first.")

            # # This might not work if the pursuer position is not
            # for pos in pursuer_positions:
            #     new_pursuer = Pursuer(pos, dynamics= 1)
            #     # print(new_pursuer)
            #     self.pursuers.append(new_pursuer)

            
            # for pos in evader_positions:
            #     status = np.random.choice([0, 1])
            #     new_evader = Evader(pos, status=status)
            #     # print(new_evader)
            #     self.evaders.append(new_evader)

            # self.activation_time = self._create_activation_timestamps()

            # if self.assignment is None:
            #     self.assignment = task_assignment()
            #     print(self.assignment)

            # self.target = target

            # self.initialized = True

            # return None

        # ==================================================
        # UPDATE POSITIONS
        # ==================================================
        for p_id, pos in enumerate(pursuer_positions):
            self.pursuers[p_id].update_position(pos)
            # print(self.pursuers[p_id])

        for e_id, pos in enumerate(evader_positions):
            self.evaders[e_id].update_position(pos)
            # print(self.evaders[e_id])

        # ==================================================
        # EVADER ACTIVATION
        # ==================================================
        initial_evader_status = self._get_evader_status()
        # print(initial_evader_status)

        print("Activation time: ",self.activation_time)
        self._update_activation()
        

        # ==================================================
        # STEP 1 — TERMINAL CONDITIONS
        # ==================================================
        if self._evaders_win():
            self.evader_wins = True

        if self._pursuers_win():
            self.pursuer_wins = True

        # ==================================================
        # STEP 2 — TASK ASSIGNMENT (EVENT-DRIVEN)
        # ==================================================

        status_changed = self.has_status_changed(initial_evader_status, self._get_evader_status())
        # print(status_changed)

        if self.assignment is None or status_changed:
            self.assignment = task_assignment()
            # print(self.assignment)
            self.apply_assignment()

        # ==================================================
        # STEP 3 — OPTIMAL CONTROL
        # ==================================================
        # Go to next position using Optimal control
        # self.print_agent(self.pursuers, "Pursuer Position Before Control")
        # self.print_agent(self.evaders, "Evader Position Before Control")

        
        self._optimal_control(target)

        self.time = self.time + 1

        # self.print_agent(self.pursuers, "Pursuer Position After Control")
        # self.print_agent(self.evaders, "Evader Position After Control")

        updated_pursuer_positions = [pursuer.position for pursuer in self.pursuers]
        updated_evader_positions = [evader.position for evader in self.evaders]

        return updated_pursuer_positions, updated_evader_positions, self.pursuer_wins, self.evader_wins

    # --------------------------------------------------
    # Optional hard reset
    # --------------------------------------------------
    def reset(self):
        self.__init__()

    def print_agent(self, agent, string):
        agent_positions = [a.position for a in agent]
        print(string, agent_positions)

    def _create_activation_timestamps(self):
        """
        Generate activation timestamps for inactive evaders using a Poisson distribution.
        
        Returns:
            inactive_evader_time (dict): A dictionary mapping inactive evader indices to their activation timestamps.
        """
        # Identify inactive evaders (status == 0) and store their indices in a NumPy array
        list_inactive_evaders = np.array([i for i, evader in enumerate(self.evaders) if evader.status == 0])
        # print("Inactive Evaders:", list_inactive_evaders)

        # Initialize the dictionary for activation timestamps
        inactive_evader_time = {}

        # If there are inactive evaders, generate their activation timestamps
        if list_inactive_evaders.size > 0:  # Use .size for NumPy arrays instead of len()
            # Dictionary comprehension to assign Poisson-distributed timestamps
            # inactive_evader_time = {evader_id: np.random.poisson(self.lambda_rate) for evader_id in list_inactive_evaders}
            activation_times = {}
            current_time = 0

            for evader_id in list_inactive_evaders:

                # Draw an inter-arrival time from Poisson(lambda)
                increment = np.random.poisson(self.lambda_rate)

                # Cumulative activation time
                current_time += increment

                activation_times[evader_id] = current_time

            inactive_evader_time = activation_times

        # Verification print
        # print(inactive_evader_time)

        return inactive_evader_time
    
    def _update_activation(self):
        """
        Update the status of inactive evaders to active when their activation time matches the current time.
        """
        # Iterate through the inactive evader times dictionary (create a list to allow safe removal during iteration)
        for evader_id, activation_time in list(self.activation_time.items()):
            # Retrieve the evader object using its ID (adjusting for 0-based indexing)
            evader = self.evaders[evader_id]

            # Check if the evader is inactive and if the current time matches its activation time
            if evader.status == 0 and self.time == activation_time:
                # Update the evader's status to active (status = 1)
                evader.status = 1

                # Optionally, remove the evader from the inactive dictionary to prevent redundant checks
                del self.activation_time[evader_id]
                print(self.activation_time)

    
    def _get_evader_status(self):

        evader_status = [evader.status for evader in self.evaders]
        evader_status_array = np.array(evader_status)

        return evader_status_array
    
    def get_evader_status(self):

        evader_status = [evader.status for evader in self.evaders]
        evader_status_array = np.array(evader_status)

        return evader_status_array
    
    def _get_observation(self):
        # Collect evader data (position and status)
        evader_positions = [evader.position for evader in self.evaders]
        evader_status = [evader.status for evader in self.evaders]

        # Collect pursuer data (position, status, dynamics)
        pursuer_positions = [pursuer.position for pursuer in self.pursuers]
        pursuer_status = [pursuer.status for pursuer in self.pursuers]
        pursuer_dynamics = [pursuer.dynamics for pursuer in self.pursuers]

        # Create observation vector
        observation = np.concatenate([
            np.array(pursuer_positions).flatten(),
            np.array(evader_positions).flatten(),
            np.array(evader_status).flatten(),
            np.array(pursuer_dynamics).flatten(),
            np.array(pursuer_status).flatten()
        ])

        return observation

    def apply_assignment(self):

        for p_idx, e_idx in enumerate(self.assignment):
            
            if e_idx != 0:
                self.pursuers[p_idx].status = 1


    
    def has_status_changed(self, old_status: np.ndarray, new_status: np.ndarray) -> bool:
        """
        Checks if there is any change between old_status and new_status arrays.

        Parameters:
        - old_status (np.ndarray): The status of evaders at the beginning of the iteration.
        - new_status (np.ndarray): The status of evaders at the end of the iteration.

        Returns:
        - bool: True if there is any change, False otherwise.
        """
        return not np.array_equal(old_status, new_status)
    
    def _get_pursuer_angle(self, target):

        # Initialize an array to hold the angles for each pursuer
        pursuer_angle = np.zeros(len(self.pursuers))

        # Get the current assignment of task for the pursuer
        assignment = np.array(self.assignment)

        # Set the target point (used for calculating intersection)
        target = np.array(target)

        # Check 
        for p_id, e_id in enumerate(self.assignment):
            
            if e_id != 0:
                pursuer_loc = self.pursuers[p_id].position
                evader_loc = self.evaders[e_id - 1].position

                R_pursuer = np.linalg.norm(pursuer_loc - target)
                R_evader = np.linalg.norm(evader_loc - target)

                position_difference = evader_loc - pursuer_loc
                distance = np.linalg.norm(position_difference)

                # Calculate game value
                B = R_evader**2 - R_pursuer**2

                # If game value B is positive, calculate the intersection point
                if B > 0:
                    t_s = (R_evader**2 - R_pursuer**2) / (2 * distance**2)
                    intersection_point = position_difference * t_s
                else:
                    # If B is non-positive, set intersection point to target
                    intersection_point = target

                direction_pursuer = intersection_point - pursuer_loc
                pursuer_angle[p_id] = np.arctan2(direction_pursuer[1], direction_pursuer[0])  # Compute angle using arctan

        return pursuer_angle
    
    def _get_evader_angle(self, target):

        # Initialize an array to store evader angles
        evader_angle = np.zeros(len(self.evaders))

        # Convert pursuer positions to an array for more efficient calculations
        p_positions = np.array([pursuer.position for pursuer in self.pursuers])
        R_P = np.linalg.norm(p_positions, axis=1)  # Vectorized norms for pursuers' locations

        # Define the origin as the target
        target = np.array(target)

        # Calculate the angle for each evader
        for i, evader in enumerate(self.evaders):
            # Calculate evader's location norm
            e_position = evader.position
            R_e = np.linalg.norm(e_position)

            B = [R_e**2 - r_p**2 for r_p in R_P]

            # Get the maximum game value and corresponding pursuer
            Barrier = np.max(B)
            p_idx = np.argmax(B)

            # Calculate position difference and Euclidean distance
            position_difference = e_position - p_positions[p_idx]
            distance = np.linalg.norm(position_difference)

            # Determin the intersection point based on game value
            if Barrier > 0:
                t_s = (R_e**2 - R_P[p_idx]**2) / (2 * distance**2)
                intersection_point = position_difference * t_s
            else:
                intersection_point = target

            # Compute angle based on direction towards the intersection
            direction_evader = intersection_point - e_position
            evader_angle[i] = np.arctan2(direction_evader[1], direction_evader[0])

        return evader_angle

    def _optimal_control(self, target):
        
        angle_pursuer = self._get_pursuer_angle(target=target)

        angle_evader = self._get_evader_angle(target=target)

        # Move Evaders
        for e_id, evader in enumerate(self.evaders):
            if evader.status == 1:
                evader_loc = evader.position
                dx = self.agent_velocity * self.dt * np.cos(angle_evader[e_id])
                dy = self.agent_velocity * self.dt * np.sin(angle_evader[e_id])
                new_location = evader_loc + np.array([dx, dy])
                self.evaders[e_id].position = new_location

        # Move Pursuers
        for p_id, pursuer in enumerate(self.pursuers):
            e_idx = self.assignment[p_id]
            if e_idx != 0:
                if self.evaders[e_idx - 1].status == 1:
                    pursuer_loc = pursuer.position
                    dx = self.agent_velocity * self.dt * np.cos(angle_pursuer[p_id])
                    dy = self.agent_velocity * self.dt * np.sin(angle_pursuer[p_id])
                    new_location = pursuer_loc + np.array([dx, dy])
                    self.pursuers[p_id].position = new_location
      
        return None
    
    def _evaders_win(self):
        for evader in self.evaders:
            distance = np.linalg.norm(evader.position - self.target)
            if distance < 0.3:
                return True
        return False
    
    def _pursuers_win(self):

        for p_idx, e_idx in enumerate(self.assignment):
            if e_idx != 0:
                pursuer = self.pursuers[p_idx]
                evader = self.evaders[e_idx - 1]
                distance = np.linalg.norm(pursuer.position - evader.position)

                capture_radius = 0.5

                if distance < capture_radius:
                    self.pursuers[p_idx].status = 0
                    self.evaders[e_idx - 1].status = -1

        
        all_evaders_captured = True
        for evader in self.evaders:
            if evader.status != -1:
                all_evaders_captured = False

        if all_evaders_captured:
            return True
        else:
            return False
        
    def get_evader_status(self):
        evader_status = []
        if len(self.evaders) > 0:
            for evader in self.evaders:
                evader_status.append(evader.status)        
            return np.array(evader_status)
        else:
            return "No evaders"
        
    def get_pursuer_status(self):
        pursuer_status = []
        if len(self.pursuers)>0:
            for pursuer in self.pursuers:
                pursuer_status.append(pursuer.status)
            return np.array(pursuer_status)
        else:
            return "No pursuers"


def task_assignment():
    
    assignment = [np.random.randint(0,3) for _ in range(3)]
    assignment = [1, 2, 3]
    assignment = [1, 2]
    print("assignment", assignment)


    return assignment








if __name__=="__main__":

    pursuer_locations = np.random.uniform(-3, 3, size=(2, 2))
    evader_locations = np.random.uniform(-3, 3, size=(2, 2))
    print(pursuer_locations)

    peg = PEGCore()

    print(peg.get_evader_status())
    
    for i in range(100):
        peg.step(pursuer_locations, evader_locations)
        print("Evader Statu:",peg.get_evader_status())
        print("Pursuer Status: ", peg.get_pursuer_status())
        print(type(peg.assignment))




    


