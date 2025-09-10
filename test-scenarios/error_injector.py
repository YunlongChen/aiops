#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIOps 错误注入器
用于在测试项目中注入各种类型的错误，模拟真实环境中的故障场景

作者: AIOps Team
创建时间: 2025-01-10
"""

import os
import random
import json
from typing import Dict, List, Any
from datetime import datetime

class ErrorInjector:
    """
    错误注入器类
    负责在不同类型的项目中注入各种错误
    """
    
    def __init__(self):
        """初始化错误注入器"""
        self.java_errors = {
            'compilation': [
                'missing_semicolon',
                'undefined_variable',
                'type_mismatch',
                'missing_import',
                'syntax_error'
            ],
            'runtime': [
                'null_pointer_exception',
                'array_index_out_of_bounds',
                'class_cast_exception',
                'out_of_memory_error',
                'stack_overflow_error'
            ],
            'build': [
                'missing_dependency',
                'version_conflict',
                'plugin_error',
                'resource_not_found'
            ]
        }
        
        self.rust_errors = {
            'compilation': [
                'borrow_checker_error',
                'lifetime_error',
                'type_mismatch',
                'missing_trait_impl',
                'macro_error'
            ],
            'runtime': [
                'panic_unwrap',
                'index_out_of_bounds',
                'thread_panic',
                'deadlock'
            ],
            'build': [
                'cargo_dependency_error',
                'feature_conflict',
                'target_error'
            ]
        }
        
        self.nodejs_errors = {
            'compilation': [
                'syntax_error',
                'reference_error',
                'type_error',
                'module_not_found'
            ],
            'runtime': [
                'uncaught_exception',
                'promise_rejection',
                'memory_leak',
                'callback_error',
                'async_error'
            ],
            'build': [
                'npm_install_error',
                'package_conflict',
                'script_error',
                'peer_dependency_error'
            ]
        }
    
    def inject_java_error(self, project_path: str, error_type: str, error_category: str) -> Dict[str, Any]:
        """
        在Java项目中注入错误
        
        Args:
            project_path: 项目路径
            error_type: 错误类型
            error_category: 错误分类 (compilation/runtime/build)
        
        Returns:
            错误注入结果
        """
        result = {
            'project_type': 'java',
            'error_category': error_category,
            'error_type': error_type,
            'injected_at': datetime.now().isoformat(),
            'files_modified': [],
            'success': False
        }
        
        try:
            if error_category == 'compilation':
                result.update(self._inject_java_compilation_error(project_path, error_type))
            elif error_category == 'runtime':
                result.update(self._inject_java_runtime_error(project_path, error_type))
            elif error_category == 'build':
                result.update(self._inject_java_build_error(project_path, error_type))
            
            result['success'] = True
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def inject_rust_error(self, project_path: str, error_type: str, error_category: str) -> Dict[str, Any]:
        """
        在Rust项目中注入错误
        
        Args:
            project_path: 项目路径
            error_type: 错误类型
            error_category: 错误分类
        
        Returns:
            错误注入结果
        """
        result = {
            'project_type': 'rust',
            'error_category': error_category,
            'error_type': error_type,
            'injected_at': datetime.now().isoformat(),
            'files_modified': [],
            'success': False
        }
        
        try:
            if error_category == 'compilation':
                result.update(self._inject_rust_compilation_error(project_path, error_type))
            elif error_category == 'runtime':
                result.update(self._inject_rust_runtime_error(project_path, error_type))
            elif error_category == 'build':
                result.update(self._inject_rust_build_error(project_path, error_type))
            
            result['success'] = True
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def inject_nodejs_error(self, project_path: str, error_type: str, error_category: str) -> Dict[str, Any]:
        """
        在Node.js项目中注入错误
        
        Args:
            project_path: 项目路径
            error_type: 错误类型
            error_category: 错误分类
        
        Returns:
            错误注入结果
        """
        result = {
            'project_type': 'nodejs',
            'error_category': error_category,
            'error_type': error_type,
            'injected_at': datetime.now().isoformat(),
            'files_modified': [],
            'success': False
        }
        
        try:
            if error_category == 'compilation':
                result.update(self._inject_nodejs_compilation_error(project_path, error_type))
            elif error_category == 'runtime':
                result.update(self._inject_nodejs_runtime_error(project_path, error_type))
            elif error_category == 'build':
                result.update(self._inject_nodejs_build_error(project_path, error_type))
            
            result['success'] = True
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _inject_java_compilation_error(self, project_path: str, error_type: str) -> Dict[str, Any]:
        """注入Java编译错误"""
        main_java_path = os.path.join(project_path, 'src', 'main', 'java', 'Main.java')
        
        error_code = {
            'missing_semicolon': 'System.out.println("Missing semicolon error")',
            'undefined_variable': 'System.out.println(undefinedVariable);',
            'type_mismatch': 'String number = 123;',
            'missing_import': 'List<String> list = new ArrayList<>();',
            'syntax_error': 'public class Main { public static void main(String[] args) { if (true { System.out.println("Syntax error"); } }'
        }
        
        if error_type in error_code:
            with open(main_java_path, 'a', encoding='utf-8') as f:
                f.write(f'\n        // Injected error: {error_type}\n')
                f.write(f'        {error_code[error_type]}\n')
        
        return {'files_modified': [main_java_path], 'error_details': f'Injected {error_type} in Main.java'}
    
    def _inject_java_runtime_error(self, project_path: str, error_type: str) -> Dict[str, Any]:
        """注入Java运行时错误"""
        main_java_path = os.path.join(project_path, 'src', 'main', 'java', 'Main.java')
        
        error_code = {
            'null_pointer_exception': 'String nullString = null; System.out.println(nullString.length());',
            'array_index_out_of_bounds': 'int[] arr = new int[5]; System.out.println(arr[10]);',
            'class_cast_exception': 'Object obj = "string"; Integer num = (Integer) obj;',
            'out_of_memory_error': 'List<byte[]> memoryEater = new ArrayList<>(); while(true) { memoryEater.add(new byte[1024*1024]); }',
            'stack_overflow_error': 'recursiveMethod();'
        }
        
        if error_type in error_code:
            with open(main_java_path, 'a', encoding='utf-8') as f:
                f.write(f'\n        // Injected runtime error: {error_type}\n')
                f.write(f'        {error_code[error_type]}\n')
                if error_type == 'stack_overflow_error':
                    f.write('    }\n    public static void recursiveMethod() { recursiveMethod(); }')
        
        return {'files_modified': [main_java_path], 'error_details': f'Injected {error_type} in Main.java'}
    
    def _inject_java_build_error(self, project_path: str, error_type: str) -> Dict[str, Any]:
        """注入Java构建错误"""
        pom_path = os.path.join(project_path, 'pom.xml')
        
        if error_type == 'missing_dependency':
            # 在代码中使用不存在的依赖
            main_java_path = os.path.join(project_path, 'src', 'main', 'java', 'Main.java')
            with open(main_java_path, 'a', encoding='utf-8') as f:
                f.write('\n        // Using non-existent dependency\n')
                f.write('        com.nonexistent.Library.doSomething();\n')
            return {'files_modified': [main_java_path], 'error_details': 'Added usage of non-existent dependency'}
        
        elif error_type == 'version_conflict':
            # 修改pom.xml创建版本冲突
            if os.path.exists(pom_path):
                with open(pom_path, 'a', encoding='utf-8') as f:
                    f.write('\n    <!-- Conflicting dependency versions -->\n')
                    f.write('    <dependency>\n')
                    f.write('        <groupId>junit</groupId>\n')
                    f.write('        <artifactId>junit</artifactId>\n')
                    f.write('        <version>3.8.1</version>\n')
                    f.write('    </dependency>\n')
                return {'files_modified': [pom_path], 'error_details': 'Added conflicting dependency version'}
        
        return {'files_modified': [], 'error_details': f'Build error {error_type} injection not implemented'}
    
    def _inject_rust_compilation_error(self, project_path: str, error_type: str) -> Dict[str, Any]:
        """注入Rust编译错误"""
        main_rs_path = os.path.join(project_path, 'src', 'main.rs')
        
        error_code = {
            'borrow_checker_error': 'let mut x = vec![1, 2, 3]; let y = &x; x.push(4); println!("{:?}", y);',
            'lifetime_error': 'fn get_str() -> &str { let s = String::from("hello"); &s }',
            'type_mismatch': 'let x: i32 = "not a number";',
            'missing_trait_impl': 'let x = CustomStruct{}; println!("{}", x);',
            'macro_error': 'println!("Missing argument: {}");'
        }
        
        if error_type in error_code:
            with open(main_rs_path, 'a', encoding='utf-8') as f:
                f.write(f'\n    // Injected error: {error_type}\n')
                f.write(f'    {error_code[error_type]}\n')
        
        return {'files_modified': [main_rs_path], 'error_details': f'Injected {error_type} in main.rs'}
    
    def _inject_rust_runtime_error(self, project_path: str, error_type: str) -> Dict[str, Any]:
        """注入Rust运行时错误"""
        main_rs_path = os.path.join(project_path, 'src', 'main.rs')
        
        error_code = {
            'panic_unwrap': 'let result: Result<i32, &str> = Err("error"); let value = result.unwrap();',
            'index_out_of_bounds': 'let vec = vec![1, 2, 3]; let item = vec[10];',
            'thread_panic': 'std::thread::spawn(|| { panic!("Thread panic!"); }).join().unwrap();',
            'deadlock': 'let mutex1 = std::sync::Arc::new(std::sync::Mutex::new(0)); let mutex2 = mutex1.clone(); std::thread::spawn(move || { let _g1 = mutex1.lock().unwrap(); let _g2 = mutex2.lock().unwrap(); });'
        }
        
        if error_type in error_code:
            with open(main_rs_path, 'a', encoding='utf-8') as f:
                f.write(f'\n    // Injected runtime error: {error_type}\n')
                f.write(f'    {error_code[error_type]}\n')
        
        return {'files_modified': [main_rs_path], 'error_details': f'Injected {error_type} in main.rs'}
    
    def _inject_rust_build_error(self, project_path: str, error_type: str) -> Dict[str, Any]:
        """注入Rust构建错误"""
        cargo_toml_path = os.path.join(project_path, 'Cargo.toml')
        
        if error_type == 'cargo_dependency_error':
            if os.path.exists(cargo_toml_path):
                with open(cargo_toml_path, 'a', encoding='utf-8') as f:
                    f.write('\n[dependencies]\n')
                    f.write('nonexistent-crate = "999.999.999"\n')
                return {'files_modified': [cargo_toml_path], 'error_details': 'Added non-existent dependency'}
        
        return {'files_modified': [], 'error_details': f'Build error {error_type} injection not implemented'}
    
    def _inject_nodejs_compilation_error(self, project_path: str, error_type: str) -> Dict[str, Any]:
        """注入Node.js编译错误"""
        index_js_path = os.path.join(project_path, 'index.js')
        
        error_code = {
            'syntax_error': 'console.log("Missing closing parenthesis"',
            'reference_error': 'console.log(undefinedVariable);',
            'type_error': 'null.someMethod();',
            'module_not_found': 'const nonExistent = require("non-existent-module");'
        }
        
        if error_type in error_code:
            with open(index_js_path, 'a', encoding='utf-8') as f:
                f.write(f'\n// Injected error: {error_type}\n')
                f.write(f'{error_code[error_type]}\n')
        
        return {'files_modified': [index_js_path], 'error_details': f'Injected {error_type} in index.js'}
    
    def _inject_nodejs_runtime_error(self, project_path: str, error_type: str) -> Dict[str, Any]:
        """注入Node.js运行时错误"""
        index_js_path = os.path.join(project_path, 'index.js')
        
        error_code = {
            'uncaught_exception': 'throw new Error("Uncaught exception");',
            'promise_rejection': 'Promise.reject(new Error("Unhandled promise rejection"));',
            'memory_leak': 'const memoryLeak = []; setInterval(() => { memoryLeak.push(new Array(1000000)); }, 100);',
            'callback_error': 'setTimeout(() => { throw new Error("Callback error"); }, 1000);',
            'async_error': 'async function errorFunc() { throw new Error("Async error"); } errorFunc();'
        }
        
        if error_type in error_code:
            with open(index_js_path, 'a', encoding='utf-8') as f:
                f.write(f'\n// Injected runtime error: {error_type}\n')
                f.write(f'{error_code[error_type]}\n')
        
        return {'files_modified': [index_js_path], 'error_details': f'Injected {error_type} in index.js'}
    
    def _inject_nodejs_build_error(self, project_path: str, error_type: str) -> Dict[str, Any]:
        """注入Node.js构建错误"""
        package_json_path = os.path.join(project_path, 'package.json')
        
        if error_type == 'npm_install_error':
            if os.path.exists(package_json_path):
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                
                if 'dependencies' not in package_data:
                    package_data['dependencies'] = {}
                
                package_data['dependencies']['non-existent-package'] = '999.999.999'
                
                with open(package_json_path, 'w', encoding='utf-8') as f:
                    json.dump(package_data, f, indent=2)
                
                return {'files_modified': [package_json_path], 'error_details': 'Added non-existent dependency'}
        
        return {'files_modified': [], 'error_details': f'Build error {error_type} injection not implemented'}
    
    def inject_random_error(self, project_path: str, project_type: str) -> Dict[str, Any]:
        """
        在项目中注入随机错误
        
        Args:
            project_path: 项目路径
            project_type: 项目类型 (java/rust/nodejs)
        
        Returns:
            错误注入结果
        """
        if project_type == 'java':
            errors = self.java_errors
        elif project_type == 'rust':
            errors = self.rust_errors
        elif project_type == 'nodejs':
            errors = self.nodejs_errors
        else:
            return {'success': False, 'error': f'Unsupported project type: {project_type}'}
        
        # 随机选择错误类别和类型
        error_category = random.choice(list(errors.keys()))
        error_type = random.choice(errors[error_category])
        
        # 注入错误
        if project_type == 'java':
            return self.inject_java_error(project_path, error_type, error_category)
        elif project_type == 'rust':
            return self.inject_rust_error(project_path, error_type, error_category)
        elif project_type == 'nodejs':
            return self.inject_nodejs_error(project_path, error_type, error_category)
    
    def get_available_errors(self, project_type: str) -> Dict[str, List[str]]:
        """
        获取指定项目类型的可用错误列表
        
        Args:
            project_type: 项目类型
        
        Returns:
            可用错误列表
        """
        if project_type == 'java':
            return self.java_errors
        elif project_type == 'rust':
            return self.rust_errors
        elif project_type == 'nodejs':
            return self.nodejs_errors
        else:
            return {}

def main():
    """主函数 - 用于测试错误注入器"""
    injector = ErrorInjector()
    
    # 显示可用的错误类型
    print("=== AIOps 错误注入器 ===")
    print("\n可用的项目类型和错误:")
    
    for project_type in ['java', 'rust', 'nodejs']:
        print(f"\n{project_type.upper()} 项目:")
        errors = injector.get_available_errors(project_type)
        for category, error_list in errors.items():
            print(f"  {category}: {', '.join(error_list)}")
    
    print("\n错误注入器已准备就绪!")
    print("使用示例:")
    print("  injector.inject_java_error('/path/to/project', 'null_pointer_exception', 'runtime')")
    print("  injector.inject_random_error('/path/to/project', 'java')")

if __name__ == '__main__':
    main()