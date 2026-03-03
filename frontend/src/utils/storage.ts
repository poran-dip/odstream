export type CameraType = "local" | "remote";

export interface BaseCamera {
  id: string;
  name: string;
  type: CameraType;
}

export interface LocalCamera extends BaseCamera {
  type: "local";
  index: number;
}

export interface RemoteCamera extends BaseCamera {
  type: "remote";
  url: string;
}

export type CameraSource = LocalCamera | RemoteCamera;

const CUSTOM_SOURCES_KEY = "customCameraSources";

export const storageUtils = {
  getCustomSources: (): CameraSource[] => {
    try {
      const saved = localStorage.getItem(CUSTOM_SOURCES_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch (error) {
      console.error("Failed to parse custom sources:", error);
      return [];
    }
  },

  saveCustomSources: (sources: CameraSource[]): void => {
    try {
      localStorage.setItem(CUSTOM_SOURCES_KEY, JSON.stringify(sources));
    } catch (error) {
      console.error("Failed to save custom sources:", error);
    }
  },

  addCustomSource: (name: string, url: string): RemoteCamera => {
    const newSource: RemoteCamera = {
      id: Date.now().toString(),
      name: name.trim(),
      type: "remote",
      url: url.trim(),
    };

    const existingSources = storageUtils.getCustomSources();
    const updatedSources = [...existingSources, newSource];
    storageUtils.saveCustomSources(updatedSources);

    return newSource;
  },

  removeCustomSource: (id: string): void => {
    const existingSources = storageUtils.getCustomSources();
    const updatedSources = existingSources.filter((source) => source.id !== id);
    storageUtils.saveCustomSources(updatedSources);
  },
};

export interface VideoSettings {
  brightness: number;
  contrast: number;
  saturation: number;
  annotateYOLO?: boolean;
}

export const DEFAULT_SETTINGS: VideoSettings = {
  brightness: 0,
  contrast: 1.0,
  saturation: 1.0,
  annotateYOLO: false,
};
