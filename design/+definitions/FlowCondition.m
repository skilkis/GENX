classdef FlowCondition < definitions.Constants
    %FLOWCONDITION Value class yielding properties of the flow
    %   Can be used to quickly obtain static/total properties at the
    %   inflow or outflow of a Stage or Turbine
    %
    %   NOTE: Mach number must be provided at a minimum to calculate other
    %   states!
    
    properties (SetAccess = private) % FIXME Update cachine to allow public
        mach                % Mach Number [-]
        a                   % Speed of Sound [m/s]
        p0                  % Total Pressure [Pa]
        p                   % Static Pressure [Pa]
        T0                  % Total Temperature [K]
        T                   % Static Temperature [K]
        rho                 % Static Density [kg/m3]
        m_dot = 8.2;        % Mass Flow [kg/s]
        V                   % Flow Velocity [m/s]
        medium              % Flow Medium 'gas' or 'air'
        s                   % Entropy TODO fix units
        h                   % Total Enthalpy TODO fix units here
    end
    
    properties (GetAccess = public, SetAccess = private)
        cache = struct()    % Caches set variables to prevent recursion
    end
    
    properties (Dependent, GetAccess = private, SetAccess = private)
        kappa               % Spec. Heat Ratio of Medium [-]
        p_ratio             % Total Pressure to Static Pressure Ratio
        t_ratio             % Total Temperature to Static Temperature Ratio
        cp                  % Specific Heat of Medium [J/kg K]
    end
    
    methods
        function obj = FlowCondition(varargin)
            % Creates optional arguments for all state variables
            args = inputParser; % Analyzes passed arguments
            exclude = fieldnames(definitions.Constants)';
            exclude = [exclude, 'cache'];
            for prop = fieldnames(obj)'
                if ~any(strcmp(exclude, prop{:}))
                    addOptional(args, prop{:}, NaN)
                end
            end
              
            % Sets result of all optional arguments for current object
            parse(args, varargin{:});   
            for field = fieldnames(args.Results)'
                obj.(field{:}) = args.Results.(field{:});
            end
        end
        
        %% Dependent property getters
        function value = get.p_ratio(obj)
            % Total Pressure to Static Pressure Ratio
            if ~isnan(obj.mach)
            value = (1 + (((obj.kappa - 1) / 2.)...
                    * obj.mach^2))^(obj.kappa / (obj.kappa - 1));
            else
                error('Mach number not provided')
            end
        end
        
        function value = get.t_ratio(obj)
            % Total Temperature to Static Temperature Ratio
            if ~isnan(obj.mach)
            value = 1 + (((obj.kappa - 1) / 2.) * obj.mach^2);
            else
                error('Mach number not provided')
            end
        end
        
        function value = get.kappa(obj)
            if strcmp(obj.medium,'air')
                value = obj.kappa_air;
            elseif strcmp(obj.medium,'gas')
                value = obj.kappa_gas;
            else
                error('No medium was specified for the FlowCondition')
            end
        end
        
        function value = get.cp(obj)
            if strcmp(obj.medium,'air')
                value = obj.cp_air;
            elseif strcmp(obj.medium,'gas')
                value = obj.cp_gas;
            else
                error('No medium was specified for the FlowCondition')
            end
        end

        %% Optional derived property getters
        function value = get.T(obj)
            % Fetches Static Temperature from Isentropic Relation
            if ~isnan(obj.cache.mach)
                func = @(obj) obj.T0 / obj.t_ratio;
                value = obj.fetcher(obj.T, func);
            elseif ~isnan(obj.cache.V)
                func = @(obj) obj.T0 - 0.5 * obj.V^2 / obj.cp_gas;
                value = obj.fetcher(obj.T, func);
            else
                error('A Mach number or Velocity must be provided')
            end
        end
        
        function value = get.T0(obj)
            % Fetches Total Temperature from Isentropic Relation
            func = @(obj) obj.t_ratio * obj.T;
            value = obj.fetcher(obj.T0, func);
        end
        
        function value = get.p(obj)
            % Fetches Static Pressure from Isentropic Relation
            func = @(obj) obj.p0 / obj.p_ratio;
            value = obj.fetcher(obj.p, func);
        end
        
        function value = get.p0(obj)
            % Fetches Total Pressure from Isentropic Relation
            func = @(obj) obj.p_ratio * obj.p;
            value = obj.fetcher(obj.p0, func);
        end
        
        function value = get.V(obj)
            % Fetches Velocity from Mach Number
            if ~isnan(obj.cache.V)
                value = obj.V;
            else
                func = @(obj) sqrt(obj.kappa * obj.gas_constant * obj.T)...
                        * obj.mach;
                value = obj.fetcher(obj.V, func);
            end
        end
        
        function obj = set.V(obj, value)
            % Fixes recursion loop caused by access to mach number
            obj = obj.update_cache('V', value);
            obj.V = value;
        end
        
        function value = get.rho(obj)
             % Fetches Density from Ideal Gas Law
            func = @(obj) obj.p / (obj.gas_constant * obj.T);
            value = obj.fetcher(obj.rho, func);
        end
        
        function value = get.mach(obj)
            if ~isnan(obj.cache.mach)
                value = obj.mach;
            else
                if ~isnan(obj.cache.V)
                    func = @(obj) obj.V / obj.a;
                    value = obj.fetcher(obj.mach, func);
                else
                    error('Mach number cannot be calculated w/o Velocity')
                end
            end
            
        end
        
        function obj = set.mach(obj, value)
            % Fixes recursion loop caused by access to mach number
            obj = obj.update_cache('mach', value);
            obj.mach = value;
        end
        
        function value = get.a(obj)
            % Fetches Speed of Sound from Static Density
            func = @(obj) sqrt(obj.kappa * obj.gas_constant * obj.T);
            value = obj.fetcher(obj.a, func);
        end
        
        %% Utility Methods
        function value = fetcher(obj, prop, func)
            % Fetches property with passed function if it is NaN
            % prop = Propert to fetch
            % func = Function on how to fetch the property
            if isnan(prop)
                value = func(obj);
                if isnan(value);
                    error(['Function: %s failed, check'...
                    'state variables'], func2str(func))
                end
            else
                value = prop;
            end
        end
        
        function obj = update_cache(obj, key, value)
            % Uses key, value pair to update cache entry
            obj.cache.(key) = value;
        end
    end
end