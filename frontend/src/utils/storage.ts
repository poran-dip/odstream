export interface CameraSource {
  id: string;
  name: string;
  url: string;
}

const CUSTOM_SOURCES_KEY = 'customCameraSources';

export const storageUtils = {
  getCustomSources: (): CameraSource[] => {
    try {
      const saved = localStorage.getItem(CUSTOM_SOURCES_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch (error) {
      console.error('Failed to parse custom sources:', error);
      return [];
    }
  },

  saveCustomSources: (sources: CameraSource[]): void => {
    try {
      localStorage.setItem(CUSTOM_SOURCES_KEY, JSON.stringify(sources));
    } catch (error) {
      console.error('Failed to save custom sources:', error);
    }
  },

  addCustomSource: (name: string, url: string): CameraSource => {
    const newSource: CameraSource = {
      id: Date.now().toString(),
      name: name.trim(),
      url: url.trim()
    };
    
    const existingSources = storageUtils.getCustomSources();
    const updatedSources = [...existingSources, newSource];
    storageUtils.saveCustomSources(updatedSources);
    
    return newSource;
  },

  removeCustomSource: (id: string): void => {
    const existingSources = storageUtils.getCustomSources();
    const updatedSources = existingSources.filter(source => source.id !== id);
    storageUtils.saveCustomSources(updatedSources);
  }
};

export interface Settings {
  brightness: number;
  contrast: number;
  saturation: number;
  annotateYOLO: boolean;
}

const SETTINGS_KEY = 'userSettings';

export const DEFAULT_SETTINGS = {
  brightness: 50,
  contrast: 50,
  saturation: 50,
  annotateYOLO: true
};

export const settingsStorage = {
  getSettings: (): Settings => {
    try {
      const saved = localStorage.getItem(SETTINGS_KEY);
      return saved ? JSON.parse(saved) : DEFAULT_SETTINGS;
    } catch (err) {
      console.error('Failed to load settings:', err);
      return DEFAULT_SETTINGS;
    }
  },

  saveSettings: (settings: Settings): void => {
    try {
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
    } catch (err) {
      console.error('Failed to save settings:', err);
    }
  },

  resetSettings: (): void => {
    localStorage.removeItem(SETTINGS_KEY);
  }
};
