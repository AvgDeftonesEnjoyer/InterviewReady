import React from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useNavigation } from '@react-navigation/native';
import { apiClient } from '../../api/client';
import { storage } from '../../utils/storage';
import { useAuthStore } from '../../store/useAuthStore';
import toast from 'react-hot-toast';
import { AnimatedInput } from '../../components/AnimatedInput';
// Google Auth via Expo
import * as WebBrowser from 'expo-web-browser';
import * as Google from 'expo-auth-session/providers/google';

WebBrowser.maybeCompleteAuthSession();

const loginSchema = z.object({
  email: z.string().email('Please enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginScreen = () => {
  const navigation = useNavigation<any>();
  const setUser = useAuthStore((state) => state.setUser);
  
  const { control, handleSubmit, setError, formState: { errors, isSubmitting } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      const response = await apiClient.post('/auth/login/', data);
      const { access, refresh, user_id, ui_language, onboarding_completed } = response.data;
      
      await storage.setAccessToken(access);
      await storage.setRefreshToken(refresh);
      
      if (ui_language) {
        await changeLanguage(ui_language);
      }
      
      setUser({ id: user_id, email: data.email }, !!onboarding_completed);
    } catch (error: any) {
      console.error('Login Error Object:', error);
      console.error('Login Response Data:', error.response?.data);
      console.error('Login Message:', error.message);
      
      let errorMessage = 'Login failed. Please check your credentials.';
      if (error.response?.data?.error) {
        const apiError = error.response.data.error;
        if (apiError === 'Email not found.') {
          setError('email', { type: 'manual', message: apiError });
          return; 
        } else if (apiError === 'Incorrect password.') {
          setError('password', { type: 'manual', message: apiError });
          return;
        } else {
          errorMessage = apiError;
        }
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message === 'Network Error') {
         errorMessage = 'Server is unreachable. Please ensure the backend is running.';
      }

      toast.error(errorMessage, { duration: 4000 });
    }
  };

  // Setup Google Auth Session
  const [request, response, promptAsync] = Google.useAuthRequest({
    webClientId: process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID || 'YOUR_WEB_CLIENT_ID',
    iosClientId: process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID || 'YOUR_IOS_CLIENT_ID',
    androidClientId: process.env.EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID || 'YOUR_ANDROID_CLIENT_ID',
  });

  // Effect to handle the Google Auth response
  React.useEffect(() => {
    if (response?.type === 'success') {
      const { authentication } = response;
      if (authentication?.idToken) {
        handleGoogleBackendLogin(authentication.idToken);
      } else {
        toast.error('Google Sign-In failed: No ID token returned.');
      }
    } else if (response?.type === 'error') {
      toast.error('Google Sign-In failed. Please try again.');
    }
  }, [response]);

  const handleGoogleBackendLogin = async (idToken: string) => {
    try {
      const res = await apiClient.post('/auth/google/', { token: idToken });
      const { access, refresh, user_id, ui_language, onboarding_completed, email } = res.data;

      await storage.setAccessToken(access);
      await storage.setRefreshToken(refresh);

      if (ui_language) {
        await changeLanguage(ui_language);
      }

      // We might not get the user's email directly from the Expo res without decoding,
      // but the backend handles it and we can just set the id state. 
      setUser({ id: user_id, email: email || 'user@example.com' }, !!onboarding_completed);
      toast.success('Successfully logged in with Google!');

    } catch (error: any) {
      console.error('Google Login Backend Error:', error);
      toast.error('Failed to authenticate with our servers.');
    }
  };

  const handleGoogleLoginPress = () => {
    promptAsync();
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Welcome Back</Text>
      
      <Controller
        control={control}
        name="email"
        render={({ field: { onChange, onBlur, value } }) => (
          <AnimatedInput
            style={[styles.input, errors.email && styles.inputError]}
            placeholder="Email"
            placeholderTextColor="#888"
            onBlur={onBlur}
            onChangeText={onChange}
            value={value}
            autoCapitalize="none"
            keyboardType="email-address"
            error={!!errors.email}
          />
        )}
      />
      {errors.email && <Text style={styles.errorText}>{errors.email.message}</Text>}

      <Controller
        control={control}
        name="password"
        render={({ field: { onChange, onBlur, value } }) => (
          <AnimatedInput
            style={[styles.input, errors.password && styles.inputError]}
            placeholder="Password"
            placeholderTextColor="#888"
            onBlur={onBlur}
            onChangeText={onChange}
            value={value}
            secureTextEntry
            error={!!errors.password}
          />
        )}
      />
      {errors.password && <Text style={styles.errorText}>{errors.password.message}</Text>}

      <TouchableOpacity 
        style={styles.primaryButton} 
        onPress={handleSubmit(onSubmit)}
        disabled={isSubmitting}
      >
        {isSubmitting ? <ActivityIndicator color="#FFF" /> : <Text style={styles.buttonText}>Sign In</Text>}
      </TouchableOpacity>

      <TouchableOpacity 
        style={styles.secondaryButton} 
        onPress={() => navigation.navigate('Register')}
      >
        <Text style={styles.secondaryButtonText}>Don't have an account? Sign Up</Text>
      </TouchableOpacity>

      <View style={styles.socialContainer}>
        <TouchableOpacity 
          style={styles.socialButton} 
          onPress={handleGoogleLoginPress}
          disabled={!request}
        >
          <Text style={styles.socialButtonText}>Google Sign-In</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.socialButton, { backgroundColor: '#000' }]}>
          <Text style={[styles.socialButtonText, { color: '#FFF' }]}>Apple Sign-In</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: '#12121D', justifyContent: 'center' },
  header: { fontSize: 32, fontWeight: '700', color: '#FFF', marginBottom: 40, textAlign: 'center' },
  input: { backgroundColor: '#1E1E2D', borderRadius: 12, padding: 16, color: '#FFF', marginBottom: 12 },
  inputError: { borderColor: '#FF4D4F', borderWidth: 1 },
  errorText: { color: '#FF4D4F', fontSize: 12, marginBottom: 12, marginLeft: 4 },
  primaryButton: { backgroundColor: '#6B4EFF', padding: 16, borderRadius: 12, alignItems: 'center', marginTop: 12 },
  buttonText: { color: '#FFF', fontWeight: '600', fontSize: 16 },
  secondaryButton: { marginTop: 24, alignItems: 'center' },
  secondaryButtonText: { color: '#A0A0A0', fontSize: 14 },
  socialContainer: { marginTop: 40, gap: 12 },
  socialButton: { backgroundColor: '#FFF', padding: 14, borderRadius: 12, alignItems: 'center' },
  socialButtonText: { color: '#000', fontWeight: '600' }
});
