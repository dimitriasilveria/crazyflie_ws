import matplotlib.pyplot as plt
import numpy as np
import random

from PEG import PEGCore

def generate_points(role= 'e' ,num_points = 3, min_distance = 5, grid_size = 15, seed = None):
        points = []
        if seed is not None:
            random.seed(seed)
        else:
            random.seed(None)

        while len(points) < num_points:
            # Generate random x and y coordinates
            x = random.uniform(-(grid_size - 1), grid_size-1)
            y = random.uniform(-(grid_size - 1), grid_size-1)
            
            # Calculate the distance from the origin
            distance = np.sqrt(x**2 + y**2)
            
            if role == 'e':
                # Check if the distance is greater than or equal to min_distance
                if distance >= min_distance:
                    points.append([x, y])

            else:
                if distance <= min_distance:
                    points.append([x, y])


        return np.array(points)



class PEGSimulation:
    def __init__(
        self,
        n_evaders=3,
        m_pursuers=3,
        xlim=5,
        ylim=5,
        dt=0.1,
        steps=200
    ):
        self.n_evaders = n_evaders
        self.m_pursuers = m_pursuers
        self.xlim = xlim
        self.ylim = ylim
        self.dt = dt
        self.steps = steps

        # Initial positions
        self.evaders = generate_points('e', self.n_evaders, 8, self.xlim)
        self.pursuers = generate_points('p', self.m_pursuers, 5.5, self.xlim)
        self.target = [0,0]

        # Simple velocity magnitudes
        self.evader_speed = 0.5
        self.pursuer_speed = 1.0

    # --------------------------------------------------
    # Simple evader motion (placeholder policy)
    # --------------------------------------------------
    def make_PEG(self,pursuer, evader, target):
        peg = PEGCore()
        peg.game_init(pursuer, evader, target)
        
        return peg

    
    def move_evaders(self):
        pass

    # --------------------------------------------------
    # Simple pursuer motion toward PEG targets
    # --------------------------------------------------
    def move_pursuers(self):
        pass

    # --------------------------------------------------
    # Plot only evaders
    # --------------------------------------------------
    def plot_evaders(self, ax):
        ax.set_xlim(-self.xlim, self.xlim)
        ax.set_ylim(-self.ylim, self.ylim)

        evader_positions = np.array(list(self.evaders))
        ax.scatter(
            evader_positions[:, 0],
            evader_positions[:, 1],
            c="red",
            label="Evaders",
            s=30,
            marker = 'x'
        )

        ax.set_title("PEG Simulation")
        # ax.legend()
        # ax.grid(True)

    # --------------------------------------------------
    # Plot only pursuers
    # --------------------------------------------------

    def plot_pursuers(self, ax):
        ax.set_xlim(-self.xlim, self.xlim)
        ax.set_ylim(-self.ylim, self.ylim)

        pursuer_positions = np.array(list(self.pursuers))
        ax.scatter(
            pursuer_positions[:, 0],
            pursuer_positions[:, 1],
            c="blue",
            label="pursuers",
            s=30
        )

        ax.set_title("PEG Simulation")
        # ax.legend()
        # ax.grid(True)

    # --------------------------------------------------
    # Main simulation loop
    # --------------------------------------------------
    def run(self):
        PEG = self.make_PEG(self.pursuers, self.evaders, self.target)
        fig, ax = plt.subplots(figsize=(4.5, 4.5))
        pursuer_wins = False
        evader_wins = False
        plt.rcParams.update({
                'text.usetex': True,
                'font.family': 'serif',
                'font.size': 10,
                'axes.labelsize': 10,
                'axes.titlesize': 10,
                'xtick.labelsize': 8,
                'ytick.labelsize': 8,
                'legend.fontsize': 8,
                'figure.dpi': 600,
                'savefig.dpi': 600,
                'pdf.fonttype': 42,
            })

        for k in range(self.steps):
            if pursuer_wins or evader_wins:
                break
            # fig.clf()
            ax.clear()
            

            # Plot
            self.plot_evaders(ax)
            self.plot_pursuers(ax)
            plt.scatter(self.target[0],self.target[1], c='green')
            
            plt.xlabel('X Position')
            plt.ylabel('Y Position')
            plt.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, -0.2),
                fontsize=8,
                ncol=3,
                frameon=False,
                handletextpad=0.4,
                columnspacing=1.0,
            )
            plt.subplots_adjust(bottom=0)
            plt.grid(True, linewidth=2, alpha=0.4)
            plt.tight_layout()            
            plt.pause(0.05)

            pursuers, evaders, pursuer_wins, evader_wins=PEG.step(self.pursuers, self.evaders, self.target)
            self.pursuers = pursuers
            self.evaders = evaders
            print(pursuer_wins, " AND ", evader_wins)


        # plt.show()

if __name__== "__main__":
    sim = PEGSimulation(
        n_evaders=2,
        m_pursuers=2,
        xlim=10,
        ylim=10,
        steps=200
    )

    sim.run()

