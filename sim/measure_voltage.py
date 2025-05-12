import numpy as np
import matplotlib.pyplot as plt
import os
import subprocess
import shutil

KHZ_VALUES = [
  0,
  10,
  50,
  100,
  250,
  500,
  1000,
  2000,
  5000,
  7500,
  10000,
  15000,
  20000,
  40000,
  62000,
  100000,
]

LAST_VALUES = 100


def run_simulation(freq_khz: int) -> float:
    """Run ngspice simulation with the specified clock frequency in kHz."""
    period_ns = 1000000 / freq_khz if freq_khz > 0 else 10000000000
    half_period_ns = period_ns / 2
    
    # Create a temporary testbench file
    temp_filename = f"testbench_{freq_khz}_khz.spice"
    
    # Copy the original testbench file
    with open("testbench_template.spice", "r") as original:
        content = original.read()
    
    # Replace the clock definition line, and add a 7.8Meg load resistor
    modified_content = content.replace(
        "{{PLACEHOLDER_CLOCK}}",
        f"{half_period_ns}n {period_ns}n"
    )
    
    # Write the modified content to the temporary file
    with open(temp_filename, "w") as temp_file:
        temp_file.write(modified_content)
    
    # Run ngspice with the temporary file
    try:
        subprocess.run(["ngspice", "-b", temp_filename], check=True)
        
        # Read the resulting voltage
        if os.path.exists("voltage.txt"):
            data = np.loadtxt("voltage.txt")
            if len(data.shape) > 1:
                voltage_data = data[:, 1]
            else:
                voltage_data = data
                
            # Calculate average of last values
            if len(voltage_data) >= LAST_VALUES:
                avg_voltage = np.mean(voltage_data[-LAST_VALUES:])
            else:
                avg_voltage = np.mean(voltage_data)
                
            return avg_voltage
        else:
            print(f"Error: voltage.txt not found after simulation with {freq_khz} kHz")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running ngspice for {freq_khz} kHz: {e}")
        return None

# Run simulations for all frequency values and collect results
results = []
for freq_khz in KHZ_VALUES:
    print(f"Running simulation for {freq_khz} kHz...")
    voltage = run_simulation(freq_khz)
    if voltage is not None:
        results.append((freq_khz, voltage))
        print(f"  Result: {voltage:.4f} V")

# Plot frequency vs voltage
if results:
    freqs, voltages = zip(*results)
    plt.figure(figsize=(10, 6))
    plt.plot(freqs, voltages, 'o-')
    plt.xscale('log')
    plt.title('Output Voltage vs. Clock Frequency')
    plt.xlabel('Frequency (kHz)')
    plt.ylabel('Output Voltage (V)')
    plt.grid(True)
    plt.savefig('freq_voltage_plot.png')
    
    # Save results to CSV
    with open('frequency_results.csv', 'w') as f:
        f.write('Frequency (kHz),Voltage (V)\n')
        for freq, voltage in results:
            f.write(f'{freq},{voltage:.6f}\n')
