from constants import Constants
import numpy as np


# TODO finish implementing all regions of the atmosphere
class ISA(Constants):

    def __init__(self, altitude=0):
        """ Calculates International Standard Atmosphere properties for the specified geo-potential altitude

        :param float altitude: Geo-potential Altitude in SI meter [m]
        """
        if 0. <= altitude <= 84852. and isinstance(altitude, float):
            self.altitude = altitude
        else:
            raise ValueError('Invalid altitude specified')

    @property
    def calculator(self):
        h, R, T0, P0, rho0 = self.altitude, self.gas_constant, self.temperature_sl, self.pressure_sl, self.rho_sl
        if h == 0:
            Talt, Palt, rhoalt = T0, P0, rho0
        elif 0 < h < 11000.:
            a = -6.5e-3
            Talt = T0 + (a * h)
            Palt = P0 * (Talt / T0) ^ (-(self.g / (a * R)))
            rhoalt = rho0 * ((Talt / T0) ^ (-((self.g / (a * R)) + 1)))
        elif 11000 <= h < 25000:
            a = -6.5e-3
            Talt = 216.66
            Palt = P0*(Talt/T0)**(-(self.g/(a*R)))
            rhoalt = 0.36480*(np.exp(-1 * ((self.g*(h-11000.))/(R * T0))))
        else:
            Talt = None
            Palt = None
            rhoalt = None
        return Talt, Palt, rhoalt


# function [T,Palt,rhoalt,a]=ISA(h)
# global Econst
# %Calculates the Temperature [K] using International Standard Atmosphere
# if(h>=0)&&(h<=11000);
#     T=Econst.Temp0+(Econst.lambda*h);
#     Palt=Econst.P0*(T/Econst.Temp0)^(-(Econst.g/(Econst.lambda*Econst.R)));
#     rhoalt=Econst.rho0*((T/Econst.Temp0)^(-((Econst.g/(Econst.lambda*Econst.R))+1)));
# elseif(h>11000)&&(h<=25000);
#     T=216.66;
#     Palt=22700*((exp(1))^(-((Econst.g*(h-11000))/(Econst.R*T))));
#     rhoalt=0.36480*((exp(1))^(-((Econst.g*(h-11000))/(Econst.R*T))));
# elseif(h>25000)&&(h<=47000);
#     T=216.66+(1*((h-20000)/1000));
#     Palt=5474.9*((216.65+(.001*(h-20000)))/216.65)^(-(Econst.g/(.001*Econst.R)));
#     rhoalt=0.088035*((216.65+(.001*(h-20000)))/216.65)^(-((Econst.g/(.001*Econst.R))-1));
# elseif(h>32000)&&(h<=47000);
#     T=228.65+(2.8*((h-32000)/1000));
#     Palt=868.02*((228.65+(0.0028*(h-32000)))/228.65)^(-(Econst.g/(0.0028*Econst.R)));
#     rhoalt=0.013225*((228.65+(0.0028*(h-32000)))/228.65)^(-((Econst.g/(0.0028*Econst.R))-1));
# elseif(h>47000)&&(h<=53000);
#     T=270.65;
#     Palt=110.91*((exp(1))^(-((Econst.g*(h-47000))/(Econst.R*270.65))));
#     rhoalt=0.001428*((exp(1))^(-((Econst.g*(h-47000))/(Econst.R*270.65))));
# elseif(h>53000)&&(h<=79000);
#     T=270.65+((-2.8)*((h-51000)/1000));
#     Palt=66.939*((270.65+(-0.0028*(h-51000)))/270.65)^(-(Econst.g/(-0.0028*Econst.R)));
#     rhoalt=0.000862*((270.65+(-0.0028*(h-51000)))/270.65)^(-((Econst.g/(-0.0028*Econst.R))-1));
# elseif(h>79000)&&(h<=90000);
#     T=214.65+((-2.0)*((h-71000)/1000));
#     Palt=3.9564*((214.65+(-0.002*(h-71000)))/214.65)^(-(Econst.g/(-0.002*Econst.R)));
#     rhoalt=0.000064*((214.65+(-0.002*(h-71000)))/214.65)^(-((Econst.g/(-0.002*Econst.R))-1));
# end
# if(h<0)||(h>84852);
#     disp('International Standard Atmosphere Calculations cannot be used for values above 84,852m')
# end
# if(h>=0)&&(h<=84852);
# a=sqrt(1.4*Econst.R*T);
# %FL=ceil(((h*1250)/381)/100);
# %disp(['Temperature at Flight Level ' num2str(FL) ' = ' num2str(T) 'K' ' = ' num2str(T-273.15) 'C'])
# %disp(['Pressure at Flight Level ' num2str(FL) ' = ' num2str(Palt/1000) 'kPa'])
# %disp(['Density at Flight Level ' num2str(FL) ' = ' num2str(rhoalt) ' [kg/m3]'])
# %disp(['Speed of Sound at Flight Level ' num2str(FL) ' = ' num2str(a) ' [m/s]'])
# end
# end

if __name__ == '__main__':
    obj = ISA(11000.)
    print(obj.altitude)
    print(obj.temperature)
