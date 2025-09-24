/**
 * Vite配置文件
 * 配置Vue开发环境和构建选项，包含性能优化配置
 * 
 * @author AI Assistant
 * @version 1.1.0
 * @date 2025-01-24
 */

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@views': resolve(__dirname, 'src/views'),
      '@assets': resolve(__dirname, 'src/assets'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@stores': resolve(__dirname, 'src/stores')
    }
  },
  server: {
    port: 5173,
    open: true,
    host: true
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    // 性能优化配置
    rollupOptions: {
      output: {
        // 代码分割配置
      manualChunks: {
        vendor: ['vue', 'vue-router'],
        utils: ['axios', 'lodash']
      },
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
      }
    },
    // 压缩配置
    minify: 'esbuild', // 使用esbuild替代terser，速度更快
    // 资源内联阈值
    assetsInlineLimit: 4096,
    // 启用CSS代码分割
    cssCodeSplit: true
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/assets/styles/variables.scss";`
      }
    }
  },
  // 依赖预构建优化
    optimizeDeps: {
      include: ['vue', 'vue-router']
    }
})