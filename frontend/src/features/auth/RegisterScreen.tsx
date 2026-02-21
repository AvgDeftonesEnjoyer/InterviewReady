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

const registerSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  email: z.string().email('Please enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type RegisterFormData = z.infer<typeof registerSchema>;

export const RegisterScreen = () => {
  const navigation = useNavigation<any>();
  const setUser = useAuthStore((state) => state.setUser);
  
  const { control, handleSubmit, formState: { errors, isSubmitting } } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      const response = await apiClient.post('/auth/register/', data);
      const { access, refresh, user_id } = response.data;
      
      await storage.setAccessToken(access);
      await storage.setRefreshToken(refresh);
      
      setUser({ id: user_id, email: data.email });
    } catch (error: any) {
      console.error('Registration Error Object:', error);
      console.error('Registration Response Data:', error.response?.data);
      console.error('Registration Message:', error.message);
      
      let errorMessage = 'Registration failed. Please try again later.';
      if (error.response?.data) {
        // DRF often returns { "email": ["This field must be unique."] } or similar
        const firstErrorKey = Object.keys(error.response.data)[0];
        if (firstErrorKey) {
            const firstErrorValue = error.response.data[firstErrorKey];
            errorMessage = `${firstErrorKey}: ${firstErrorValue}`;
        }
      } else if (error.message === 'Network Error') {
         errorMessage = 'Server is unreachable. Please ensure the backend is running.';
      }
      
      toast.error(errorMessage, { duration: 4000 });
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Create Account</Text>
      
      <Controller
        control={control}
        name="username"
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            style={[styles.input, errors.username && styles.inputError]}
            placeholder="Username"
            placeholderTextColor="#888"
            onBlur={onBlur}
            onChangeText={onChange}
            value={value}
            autoCapitalize="none"
          />
        )}
      />
      {errors.username && <Text style={styles.errorText}>{errors.username.message}</Text>}

      <Controller
        control={control}
        name="email"
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            style={[styles.input, errors.email && styles.inputError]}
            placeholder="Email"
            placeholderTextColor="#888"
            onBlur={onBlur}
            onChangeText={onChange}
            value={value}
            autoCapitalize="none"
            keyboardType="email-address"
          />
        )}
      />
      {errors.email && <Text style={styles.errorText}>{errors.email.message}</Text>}

      <Controller
        control={control}
        name="password"
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            style={[styles.input, errors.password && styles.inputError]}
            placeholder="Password"
            placeholderTextColor="#888"
            onBlur={onBlur}
            onChangeText={onChange}
            value={value}
            secureTextEntry
          />
        )}
      />
      {errors.password && <Text style={styles.errorText}>{errors.password.message}</Text>}

      <TouchableOpacity 
        style={styles.primaryButton} 
        onPress={handleSubmit(onSubmit)}
        disabled={isSubmitting}
      >
        {isSubmitting ? <ActivityIndicator color="#FFF" /> : <Text style={styles.buttonText}>Sign Up</Text>}
      </TouchableOpacity>

      <TouchableOpacity 
        style={styles.secondaryButton} 
        onPress={() => navigation.goBack()}
      >
        <Text style={styles.secondaryButtonText}>Already have an account? Sign In</Text>
      </TouchableOpacity>
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
  secondaryButtonText: { color: '#A0A0A0', fontSize: 14 }
});
