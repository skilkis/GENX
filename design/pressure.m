function p_end = pressure(t_ratio, p_start)
global kappa eta_tt
p_end = p_start * ((1 + (1/eta_tt)*(t_ratio - 1))^(kappa/(kappa-1)));
end

