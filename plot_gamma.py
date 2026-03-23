import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import default_params

from classes.game import Game
from strategies import TitForTat, QLearningStrategy

def main():
    num_turns = 100000

    import matplotlib.cm as cm
    gammas = [0.1, 0.2, 0.3, 1/3, 0.4, 0.6, 0.8, 0.99]
    colors = cm.coolwarm(np.linspace(1, 0, len(gammas)))

    fig, ax1 = plt.subplots(figsize=(10, 6))

    for gamma, color in zip(gammas, colors):
        print(f"\nRunning gamma={gamma:.3f}")
        ql_params = {
            "alpha"         : 0.1,    
            "gamma"         : gamma,    
            "epsilon"       : 1.0,     
            "epsilon_min"   : 0.01,    
            "epsilon_decay" : 0.9999, 
        }
        
        strategy_mix = {
            TitForTat: 0.5,
            QLearningStrategy: 0.5
        }
        
        game = Game(num_players=2, num_turns=num_turns, strategy_mix=strategy_mix, ql_params=ql_params)
        game.play()
        
        ql_agent = [a for a in game.players.values() if isinstance(a.get_strategy(), QLearningStrategy)][0]
        hist = ql_agent.get_strategy().history
        
        T = len(hist["action"])
        window = max(200, T // 100)
        
        actions_bin = np.array([1 if a == "C" else 0 for a in hist["action"]], dtype=float)
        coop_rate = np.convolve(actions_bin, np.ones(window) / window, mode="valid")
        turns_roll = np.arange(window, T + 1)
        
        if abs(gamma - 1/3) < 1e-5:
            ax1.plot(turns_roll, coop_rate, label="γ = 1/3 (Threshold)", color='black', lw=2, linestyle='--')
        else:
            ax1.plot(turns_roll, coop_rate, label=f"γ = {gamma:.2f}", color=color, lw=1.5)

    ax1.set_title("Impact of Discount Factor (γ) on convergence against TitForTat (100K turns)")
    ax1.set_xlabel("Turn")
    ax1.set_ylabel(f"Cooperation rate (window={window})")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    output_path = "gamma_impact.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"\nSaved {os.path.abspath(output_path)}")

if __name__ == "__main__":
    main()
