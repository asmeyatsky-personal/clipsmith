import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'app.clipsmith',
  appName: 'Clipsmith',
  webDir: 'out',
  ios: {
    contentInset: 'automatic',
    backgroundColor: '#000000',
    scheme: 'Clipsmith',
  },
  server: {
    androidScheme: 'https',
    iosScheme: 'capacitor',
    // For dev, point to the running Next dev server: NEXT_PUBLIC_DEV_SERVER=http://192.168.x.x:3000
    // url: process.env.CAP_SERVER_URL,
    cleartext: false,
  },
  plugins: {
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert'],
    },
  },
};

export default config;
