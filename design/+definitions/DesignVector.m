classdef DesignVector < dynamicprops
    %DESIGNVECTOR Summary of this class goes here
    %   Detailed explanation goes here
    % TODO add explanation here

    properties
        x0                      % Initial Values of the Design Vector
        keys                    % Design Names
    end
    
    methods
        
%     function obj = DesignVector(psi, phi, R, N)
%         obj.psi = psi; obj.phi = phi; obj.R = R; obj.N = N;
%         obj.vector = [psi, phi, R, N];
%     end

        function obj = DesignVector(x0, keys)

            obj.x0 = x0;
            obj.keys = keys;

            index = 1;
            for key = keys'
                P = addprop(obj, key{:});
                P.GetMethod = @(x) obj.data(index);
                index = index + 1;
            end
        end

    %  function obj = DesignVector(data, keys)
    %      if nargin == 0
    %         data = 0;
    %         keys = '';
    %      elseif nargin == 1
    %         keys = '';
    %      end
    %      obj = obj@double(data);
    %      obj.keys = keys;
    %   end
   
%       function sref = subsref(obj,s)
%         switch s(1).type
%            case '.'
%               switch s(1).subs
%                  case 'keys'
%                     sref = obj.keys;
%                  case 'Data'
%                     d = double(obj);
%                     if length(s)<2
%                        sref = d;
%                     elseif length(s)>1 && strcmp(s(2).type,'()')
%                        sref = subsref(d,s(2:end));
%                     end
%                  otherwise
%                     error('Not a supported indexing expression')
%               end
%            case '()'
%               d = double(obj);
%               newd = subsref(d,s(1:end));
%               sref = definitions.DesignVector(newd,obj.keys);
%            case '{}'
%               error('Not a supported indexing expression')
%         end
%      end
     
%      function obj = subsasgn(obj,s,b)
%         switch s(1).type
%            case '.'
%               switch s(1).subs
%                  case 'keys'
%                     obj.keys = b;
%                  case 'Data'
%                     if length(s)<2
%                        obj = definitions.DesignVector(b,obj.keys);
%                     elseif length(s)>1 && strcmp(s(2).type,'()')
%                        d = double(obj);
%                        newd = subsasgn(d,s(2:end),b);
%                        obj = definitions.DesignVector(newd,obj.keys);
%                     end
%                  otherwise
%                     error('Not a supported indexing expression')
%               end
%            case '()'
%               d = double(obj);
%               newd = subsasgn(d,s(1),b);
%               obj = definitions.DesignVector(newd,obj.keys);
%            case '{}'
%               error('Not a supported indexing expression')
%         end
%      end
     
%      function newobj = horzcat(varargin)
%         d1 = cellfun(@double,varargin,'UniformOutput',false );
%         data = horzcat(d1{:});
%         str = horzcat(cellfun(@char,varargin,'UniformOutput',false));
%         newobj = definitions.DesignVector(data,str);
%      end
     
%      function newobj = vertcat(varargin)
%         d1 = cellfun(@double,varargin,'UniformOutput',false );
%         data = vertcat(d1{:});
%         str = vertcat(cellfun(@char,varargin,'UniformOutput',false));
%         newobj = definitions.DesignVector(data,str);
%      end
     
%      function str = char(obj)
%         str = obj.keys;
%      end
     
%      function disp(obj)
%         disp(obj.keys)
%         disp(double(obj))
%      end
  end
end
