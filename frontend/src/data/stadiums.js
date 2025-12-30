// AFCON 2025 Morocco Stadium Data
export const STADIUMS = [
  {
    id: 'prince-moulay-abdellah',
    name: 'Prince Moulay Abdellah Stadium',
    city: 'Rabat',
    capacity: 69500,
    image: '/stadiums/rabat-main.jpg',
    description: 'Main stadium in Rabat, one of the largest venues for AFCON 2025'
  },
  {
    id: 'complexe-olympique-rabat',
    name: 'Complexe Sportif Prince Moulay Abdellah Olympic Stadium',
    city: 'Rabat',
    capacity: 21000,
    image: '/stadiums/rabat-olympic.jpg',
    description: 'Olympic complex stadium in Rabat'
  },
  {
    id: 'prince-heritier-rabat',
    name: 'Complexe Sportif Prince Heritier Moulay El Hassan',
    city: 'Rabat',
    capacity: 22000,
    image: '/stadiums/rabat-heritier.jpg',
    description: 'Prince Heritier sports complex in Rabat'
  },
  {
    id: 'el-barid-rabat',
    name: 'Stade El Barid',
    city: 'Rabat',
    capacity: 18000,
    image: '/stadiums/rabat-barid.jpg',
    description: 'El Barid Stadium in Rabat'
  },
  {
    id: 'grand-agadir',
    name: 'Grande Stade d\'Agadir',
    city: 'Agadir',
    capacity: 45480,
    image: '/stadiums/agadir.jpg',
    description: 'Grand Stadium of Agadir, major venue in southern Morocco'
  },
  {
    id: 'complexe-fes',
    name: 'Complexe Sportif de Fes',
    city: 'Fes',
    capacity: 45000,
    image: '/stadiums/fes.jpg',
    description: 'Sports complex in the historic city of Fes'
  },
  {
    id: 'grand-marrakech',
    name: 'Grande Stade de Marrakech',
    city: 'Marrakech',
    capacity: 45240,
    image: '/stadiums/marrakech.jpg',
    description: 'Grand Stadium of Marrakech, the Red City venue'
  },
  {
    id: 'mohammed-v-casa',
    name: 'Stade Mohammed V',
    city: 'Casablanca',
    capacity: 67000,
    image: '/stadiums/casablanca.jpg',
    description: 'Historic Mohammed V Stadium in Casablanca'
  },
  {
    id: 'grand-tangier',
    name: 'Grande Stade de Tangier',
    city: 'Tangier',
    capacity: 68000,
    image: '/stadiums/tangier.jpg',
    description: 'Grand Stadium of Tangier, northern Morocco venue'
  }
];

// Stadium resource configurations based on capacity
export const getStadiumResources = (capacity) => {
  const ratio = capacity / 50000;
  return {
    securityGates: Math.max(20, Math.round(30 * ratio)),
    turnstiles: Math.max(15, Math.round(25 * ratio)),
    vendors: Math.max(30, Math.round(50 * ratio)),
    exitGates: Math.max(20, Math.round(30 * ratio))
  };
};

// AFCON 2025 Morocco Theme Colors
export const THEME = {
  primary: '#C1272D',      // Moroccan Red
  secondary: '#006233',     // Moroccan Green
  accent: '#FFD700',        // Gold accent
  dark: '#1a1a2e',
  darker: '#16213e',
  light: '#f5f5f5',
  white: '#ffffff',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#3b82f6'
};

// Simulation defaults
export const SIM_DEFAULTS = {
  matchDuration: 120,       // minutes
  preMatchWindow: 180,      // minutes before kickoff
  postMatchWindow: 60,      // minutes after match
  kickoffTime: 180,         // simulation time when match starts
  arrivalPeakBefore: 60     // peak arrivals 60 min before kickoff
};
