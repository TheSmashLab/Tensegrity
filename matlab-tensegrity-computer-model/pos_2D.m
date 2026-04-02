% Code for a 2D tensegrity Structure
% Inputs: initial positions, initial lengths, external forces, which nodes
% are fixed in which directions
% Outputs: final positions
% Version 0.1 by Caleb Swain on 2023/11/13

close all % close all open plots
clear % clears the workspace

% create a vector of positions
x1 = [0; 0]; % x and y position of node 1
x2 = [1; 1]; % x and y position of node 2
x3 = [1; 0]; % x and y position of node 3
x4 = [0; 1]; % x and y position of node 4

p = [x1, x2, x3, x4]; % position vector with columns as nodes, row 1: x, row 2: y

rod1 = [x1, x2];
rod2 = [x3, x4];

cable1 = [x1, x3];
cable2 = [x2, x3];
cable3 = [x2, x4];
cable4 = [x1, x4];

hold on
plot(rod1(1,:), rod1(2,:), "o-r")
plot(rod2(1,:), rod2(2,:), "o-r")
plot(cable1(1,:), cable1(2,:), ".-c")
plot(cable2(1,:), cable2(2,:), ".-c")
plot(cable3(1,:), cable3(2,:), ".-c")
plot(cable4(1,:), cable4(2,:), ".-c")
hold off

pause(5)

Lr1 = sqrt((rod1(1,2)-rod1(1,1))^2+(rod1(2,2)-rod1(2,1))^2); % length of rod 1
Lr2 = sqrt((rod2(1,2)-rod2(1,1))^2+(rod2(2,2)-rod2(2,1))^2); % length of rod 2

Lc1 = sqrt((cable1(1,2)-cable1(1,1))^2+(cable1(2,2)-cable1(2,1))^2); % length of cable 1
Lc2 = sqrt((cable2(1,2)-cable2(1,1))^2+(cable2(2,2)-cable2(2,1))^2); % length of cable 2
Lc3 = sqrt((cable3(1,2)-cable3(1,1))^2+(cable3(2,2)-cable3(2,1))^2); % length of cable 3
Lc4 = sqrt((cable4(1,2)-cable4(1,1))^2+(cable4(2,2)-cable4(2,1))^2); % length of cable 4

% pick up here
% R =  % rigidity matrix
error = 1; tol = 0.001;
while error > tol
    % calculate the rigidity matrix
    error = error/10; % temp way to guarantee error gets smaller than tol.
end

