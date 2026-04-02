clear
clc

a = arduino('/dev/cu.usbserial-110','Nano3'); % Set COM port
x_label = 'Time (sec)';
y_label = 'Resistance (ohms)';

delay = 0.1;
time_resolution = 0.1; % Time resolution in seconds

time = (0:time_resolution:100); % Assuming a maximum time of 100 seconds, adjust as needed
resistance1Array = zeros(size(time)); % Preallocate resistance arrays with the same size as time
resistance2Array = zeros(size(time));
resistance3Array = zeros(size(time));
resistance4Array = zeros(size(time));

count = 0;

plotGraph = plot(time, resistance1Array, 'r');
hold on
plotGraph1 = plot(time, resistance2Array, 'b');
plotGraph2 = plot(time, resistance3Array, 'g');
plotGraph3 = plot(time, resistance4Array, 'k');

legend('Sensor 1', 'Sensor 2', 'Sensor 3', 'Sensor 4');
xlabel(x_label);
ylabel(y_label);

tic; % Start timer

while ishandle(plotGraph)
    count = count + 1;
    
    % Read sensor voltages
    voltage1 = readVoltage(a, 'A0');
    voltage2 = readVoltage(a, 'A1');
    voltage3 = readVoltage(a, 'A2');
    voltage4 = readVoltage(a, 'A3');
    
    % Calculate resistance using Ohm's law (R = V/I)
    % Assuming known resistor values for voltage dividers
    resistor1 = 220; % Resistance of resistor in series with sensor 1 (in ohms)
    resistor2 = 220; % Resistance of resistor in series with sensor 2 (in ohms)
    resistor3 = 220; % Resistance of resistor in series with sensor 3 (in ohms)
    resistor4 = 220; % Resistance of resistor in series with sensor 4 (in ohms)

    resistance1 = voltage1 * (resistor1 / (5 - voltage1)); % Calculate resistance using voltage divider formula
    resistance2 = voltage2 * (resistor2 / (5 - voltage2));
    resistance3 = voltage3 * (resistor3 / (5 - voltage3));
    resistance4 = voltage4 * (resistor4 / (5 - voltage4));
    
    % Update resistance arrays
    resistance1Array(count) = resistance1;
    resistance2Array(count) = resistance2;
    resistance3Array(count) = resistance3;
    resistance4Array(count) = resistance4;

    % Update plot data
    set(plotGraph, 'YData', resistance1Array)
    set(plotGraph1, 'YData', resistance2Array)
    set(plotGraph2, 'YData', resistance3Array)
    set(plotGraph3, 'YData', resistance4Array)

    drawnow;
    pause(delay);
end
