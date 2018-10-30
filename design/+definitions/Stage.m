classdef Stage < definitions.Constants
    %Stage Value class inter-stage properties

    % Variables:
    % U = Peripheral Velocity [m/s]
    % c = Absolute Velocity [m/s]
    % w = Relative Velocity [m/s]

    % Subscripts: 
    % x = Axial Velocity
    % 1 = Nozzle Inlet
    % 2 = Rotor Inflow
    % 3 = Rotor Outflow

    properties (SetAccess = private)
        w                       % Specific Work Expected of the Stage
        omega                   % Angular Velocity at Mean Radius [rad/s]
        psi                     % Stage Loading Coefficient [-]
        phi                     % Flow Coefficient [-]
        R                       % Degree of Reaction [-]
        inflow                  % Inflow State Variables
        index                   % Order of the stage within the Turbine
        A                       % Aspect Ratio H/l
    end
    
    properties (Dependent, SetAccess = private)
        U                       % Perhipheral Velocity [m/s]
        r_m                     % Mean Radius
        c_x                     % Axial velocity
        c_1                     % Absolute Velocity at Nozzle Inflow
        c_2                     % Absolute Velocity at Rotor Inflow
        w_2                     % Relative Velocity at Rotor Inflow
        w_3                     % Relative Velocity at Rotor Outflow
        alpha_1                 % Abs. Flow Angle at Nozzle Inflow [rad]
        alpha_2                 % Abs. Flow Angle at Rotor Inflow [rad]
        beta_2                  % Rel. Flow Angle at Rotor Inflow [rad]
        beta_3                  % Rel. Flow Angle at Rotor
        zeta_n                  % Nozzle Solderberg Loss Coefficient [-]
        zeta_r                  % Rotor Solderberg Loss Coefficient [-]
        eta_tt                  % Estimated Total-to-Total Efficiency [-]
        intflow                 % Intermediate Flow State Variables [-]
        outflow                 % Outflow State Variables [-]
    end
    
    methods
        function obj = Stage(varargin)
            % Creates optional arguments for all state variables
            args = inputParser; % Analyzes passed arguments
            
            % TODO clean this up with either turbine_in or struct input
            addRequired(args, 'inflow', @definitions.Validators.validFlow)
            addRequired(args, 'omega')
            addRequired(args, 'psi')
            addRequired(args, 'phi')
            addRequired(args, 'R')
            addRequired(args, 'w')
            addOptional(args, 'index', 1)
            parse(args, varargin{:});   
            for field = fieldnames(args.Results)'
                obj.(field{:}) = args.Results.(field{:});
            end
        end

        function f = plotVelocityDiagram(obj)
            f = figure('Name', 'VelocityDiagram');
            hold on; grid on;
            c2 = obj.c_2 / obj.U;
            w2 = obj.w_2 / obj.U;
            c3 = obj.c_1 / obj.U; % c_1 = c_3 due to repeating stage
            w3 = obj.w_3 / obj.U;

            % Drawing Arrows
            q_1 = quiver(0, 0, ...
                         -c2 * sin(obj.alpha_2), c2 * cos(obj.alpha_2), 0);
            q_2 = quiver(0, 0,...
                         -w2 * sin(obj.beta_2), w2 * cos(obj.beta_2), 0);
            q_3 = quiver(0, 0,...
                         c3 * sin(obj.alpha_1), c3 * cos(obj.alpha_1), 0);
            q_4 = quiver(0, 0,...
                         w3 * sin(obj.beta_3), w3 * cos(obj.beta_3), 0);
            q_5 = quiver(-w2 * sin(obj.beta_2), w2 * cos(obj.beta_2),...
                         -1, 0, 0, 'Color', [0 0.6 0.3]);
            q_6 = quiver(w3 * sin(obj.beta_3), w3 * cos(obj.beta_3),...
                         -1, 0, 0, 'Color', [0 0.6 0.3]);

            % Setting Velocity Diagram Formatting
            q_vector = [q_1, q_2, q_3, q_4, q_5, q_6];
            property_cell = {'LineWidth', 'MaxHeadSize'};
            [value_cell{1:length(q_vector), 1}] = deal(2.0);
            [value_cell{1:length(q_vector), 2}] = deal(0.1);
            set(q_vector, property_cell, value_cell)
            clear value_cell

            set(gca,'Xdir', 'reverse','Ydir','reverse')
            l = legend('$c_2$', '$w_2$', '$c_3$', '$w_3$', '$U$');
            x = xlabel('Normalized Tangential Velocity');
            y = ylabel('Normalized Axial Velocity');
            t = title(['Velocity Diagram $\left( \psi=' num2str(obj.psi)... 
                       ', \phi=' num2str(obj.phi)...
                       ', R=' num2str(obj.R) '\right)$']);

            prop_vector = [l, x, y, t];
            property_cell = {'Interpreter', 'FontSize'};
            [value_cell{1:length(prop_vector), 1}] = deal('latex');
            [value_cell{1:length(prop_vector), 2}] = deal(12);
            set(prop_vector, property_cell, value_cell)
            f.GraphicsSmoothing = 'on';
            utilities.savefig(f)
        end
    end

    methods

        function value = get.U(obj)
            value = sqrt(obj.w / obj.psi);
        end

        function value = get.r_m(obj)
            value = obj.U / obj.omega;
        end

        function value = get.alpha_1(obj)
            value = atan((obj.R - 1 + 0.5*obj.psi) / obj.phi);
        end

        function value = get.alpha_2(obj)
            value = atan((1 - obj.R + 0.5*obj.psi) / obj.phi);
        end

        function value = get.beta_2(obj)
            value = atan((0.5*obj.psi - obj.R) / obj.phi);
        end
        
        function value = get.beta_3(obj)
            value = atan((0.5*obj.psi + obj.R) / obj.phi);
        end

        function value = get.c_x(obj)
            value = obj.U * obj.phi;
        end

        function value = get.c_1(obj)
            value = obj.c_x / cos(obj.alpha_1);
        end

        function value = get.c_2(obj)
            value = obj.c_x / cos(obj.alpha_2);
        end

        function value = get.w_2(obj)
            value = obj.c_x / cos(obj.beta_2);
        end

        
        function value = get.w_3(obj)
            value = obj.c_x / cos(obj.beta_3);
        end

        function value = get.zeta_n(obj)
            % Nozzle Solderberg Loss Coefficient
            epsilon_n = rad2deg(obj.alpha_2);
            value = obj.getLossCoefficient(epsilon_n);
        end

        function value = get.zeta_r(obj)
            % Rotor Solderberg Loss Coefficient
            epsilon_n = rad2deg(obj.beta_2 + obj.beta_3);
            value = obj.getLossCoefficient(epsilon_n);
        end

        function value = get.eta_tt(obj)
            % Estimates stage total-to-total efficiency w/ 
            value = 1/(1 + (obj.zeta_r*(obj.w_3^2) + ...
                    obj.zeta_n*(obj.c_2^2))/(2*obj.w));
        end

        function value = get.outflow(obj)
            in = obj.inflow;
%             value = definitions.FlowCondition('mach', in.mach,...
%                                               'a', in.a,...
%                                               'p0', in.p0,...
%                                               'p', in.p,...
%                                               'T0', in.T0,...
%                                               'T', in.T,...
%                                               'rho', in.rho,...
%                                               'm_dot', in.m_dot,...
%                                               'V', in.V,...
%                                               'medium', in.medium,...
%                                               's', in.s,...
%                                               'h', in.h);
            
            % Calculates new states
            T0 = in.T0 - (obj.w / in.cp);
            p0 = in.p0 * ((1 + ((1/obj.eta_tt) *((T0/in.T0) -...
             1.)))^(in.kappa /(in.kappa - 1.)));
            s = in.s + in.cp*log(T0/in.T0) - in.gas_constant*log(p0/in.p0);
            h = in.h + in.cp/1000*(T0-in.T0);
             
            value = definitions.FlowCondition('p0', p0,...
                                              'T0', T0,...
                                              'm_dot', in.m_dot,...
                                              'V', in.V,...
                                              'medium', in.medium,...
                                              's', s,...
                                              'h', h);
        end
    end

    methods (Static)
        function value = getLossCoefficient(epsilon)
            % Solderberg Loss Coefficient for simplified case Re = 10e5 &
            % Blade H/l = 3. Input epsilon is in SI degree [deg]
            value = 0.04 * (1 + 1.5 * (epsilon/ 100)^2);
        end
    end
    
end

