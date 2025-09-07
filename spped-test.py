import time
import statistics
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from ollama import Client
from ollama._types import ChatResponse
import ollama
from tools import read_file, list_files, edit_file, run_command, todo_write_tool, grep_tool, glob_tool, read_many_files
from system_prompt import system_prompt

@dataclass
class GenerationResult:
    """Data class to store generation test results"""
    prompt: str
    response_length: int
    generation_time: float
    tokens_per_second: float
    first_token_time: float
    model: str
    timestamp: float

class GenerationSpeedTester:
    """Test generation speed for different models and prompts"""
    
    def __init__(self, model: str = 'qwen3:8b'):
        self.model = model
        self.results: List[GenerationResult] = []
        
        # Test prompts of varying complexity
        self.test_prompts = [
            "Hello, how are you?",
            "Write a short Python function to calculate fibonacci numbers.",
            "Explain the concept of machine learning in 3 paragraphs.",
            "Write a complete React component for a todo list with add, edit, and delete functionality.",
            "Create a detailed business plan for a tech startup including market analysis, financial projections, and marketing strategy."
        ]
    
    def measure_generation_speed(self, prompt: str, verbose: bool = True) -> GenerationResult:
        """Measure generation speed for a single prompt"""
        if verbose:
            print(f"\n{'='*60}")
            print(f"Testing: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
            print(f"Model: {self.model}")
            print(f"{'='*60}")
        
        # Prepare messages
        messages = [{
            "role": "system",
            "content": system_prompt
        }, {
            "role": "user", 
            "content": prompt
        }]
        
        # Start timing
        start_time = time.time()
        first_token_time = None
        
        # Generate response with streaming
        stream = ollama.chat(
            model=self.model, 
            messages=messages, 
            stream=True
        )
        
        full_content = ""
        token_count = 0
        
        if verbose:
            print("Response: ", end='', flush=True)
        
        for chunk in stream:
            if chunk.message.content:
                if first_token_time is None:
                    first_token_time = time.time() - start_time
                
                content = chunk.message.content
                full_content += content
                token_count += len(content.split())  # Rough token estimation
                
                if verbose:
                    print(content, end='', flush=True)
        
        end_time = time.time()
        generation_time = end_time - start_time
        tokens_per_second = token_count / generation_time if generation_time > 0 else 0
        
        if verbose:
            print(f"\n\nGeneration completed in {generation_time:.2f}s")
            print(f"Response length: {len(full_content)} characters")
            print(f"Estimated tokens: {token_count}")
            print(f"Tokens per second: {tokens_per_second:.2f}")
            print(f"Time to first token: {first_token_time:.3f}s")
        
        result = GenerationResult(
            prompt=prompt,
            response_length=len(full_content),
            generation_time=generation_time,
            tokens_per_second=tokens_per_second,
            first_token_time=first_token_time or 0,
            model=self.model,
            timestamp=time.time()
        )
        
        self.results.append(result)
        return result
    
    def run_comprehensive_test(self, iterations: int = 3) -> Dict[str, Any]:
        """Run comprehensive speed tests across all prompts"""
        print(f"\n🚀 Starting comprehensive generation speed test")
        print(f"Model: {self.model}")
        print(f"Iterations per prompt: {iterations}")
        print(f"Total tests: {len(self.test_prompts) * iterations}")
        
        all_results = []
        
        for i, prompt in enumerate(self.test_prompts):
            print(f"\n📝 Testing prompt {i+1}/{len(self.test_prompts)}")
            prompt_results = []
            
            for iteration in range(iterations):
                print(f"\n  Iteration {iteration + 1}/{iterations}")
                result = self.measure_generation_speed(prompt, verbose=True)
                prompt_results.append(result)
                all_results.append(result)
                
                # Small delay between iterations
                time.sleep(1)
        
        return self.analyze_results(all_results)
    
    def analyze_results(self, results: List[GenerationResult]) -> Dict[str, Any]:
        """Analyze and summarize test results"""
        if not results:
            return {}
        
        # Overall statistics
        generation_times = [r.generation_time for r in results]
        tokens_per_second = [r.tokens_per_second for r in results]
        first_token_times = [r.first_token_time for r in results]
        response_lengths = [r.response_length for r in results]
        
        analysis = {
            "model": self.model,
            "total_tests": len(results),
            "overall_stats": {
                "avg_generation_time": statistics.mean(generation_times),
                "median_generation_time": statistics.median(generation_times),
                "min_generation_time": min(generation_times),
                "max_generation_time": max(generation_times),
                "std_generation_time": statistics.stdev(generation_times) if len(generation_times) > 1 else 0,
                
                "avg_tokens_per_second": statistics.mean(tokens_per_second),
                "median_tokens_per_second": statistics.median(tokens_per_second),
                "max_tokens_per_second": max(tokens_per_second),
                
                "avg_first_token_time": statistics.mean(first_token_times),
                "median_first_token_time": statistics.median(first_token_times),
                "min_first_token_time": min(first_token_times),
                
                "avg_response_length": statistics.mean(response_lengths),
                "total_characters_generated": sum(response_lengths)
            }
        }
        
        # Per-prompt analysis
        prompt_stats = {}
        for prompt in self.test_prompts:
            prompt_results = [r for r in results if r.prompt == prompt]
            if prompt_results:
                prompt_times = [r.generation_time for r in prompt_results]
                prompt_tps = [r.tokens_per_second for r in prompt_results]
                
                prompt_stats[prompt] = {
                    "iterations": len(prompt_results),
                    "avg_time": statistics.mean(prompt_times),
                    "avg_tokens_per_second": statistics.mean(prompt_tps),
                    "consistency": 1 - (statistics.stdev(prompt_times) / statistics.mean(prompt_times)) if len(prompt_times) > 1 else 1
                }
        
        analysis["per_prompt_stats"] = prompt_stats
        
        return analysis
    
    def print_summary(self, analysis: Dict[str, Any]):
        """Print a formatted summary of test results"""
        if not analysis:
            print("No results to summarize")
            return
        
        stats = analysis["overall_stats"]
        
        print(f"\n{'='*80}")
        print(f"📊 GENERATION SPEED TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Model: {analysis['model']}")
        print(f"Total tests: {analysis['total_tests']}")
        print(f"Total characters generated: {stats['total_characters_generated']:,}")
        
        print(f"\n⏱️  GENERATION TIME STATISTICS:")
        print(f"  Average: {stats['avg_generation_time']:.2f}s")
        print(f"  Median:  {stats['median_generation_time']:.2f}s")
        print(f"  Range:   {stats['min_generation_time']:.2f}s - {stats['max_generation_time']:.2f}s")
        print(f"  Std Dev: {stats['std_generation_time']:.2f}s")
        
        print(f"\n🚀 TOKENS PER SECOND:")
        print(f"  Average: {stats['avg_tokens_per_second']:.2f}")
        print(f"  Median:  {stats['median_tokens_per_second']:.2f}")
        print(f"  Peak:    {stats['max_tokens_per_second']:.2f}")
        
        print(f"\n⚡ FIRST TOKEN LATENCY:")
        print(f"  Average: {stats['avg_first_token_time']:.3f}s")
        print(f"  Median:  {stats['median_first_token_time']:.3f}s")
        print(f"  Best:    {stats['min_first_token_time']:.3f}s")
        
        print(f"\n📝 PER-PROMPT BREAKDOWN:")
        for prompt, prompt_stats in analysis["per_prompt_stats"].items():
            print(f"  {prompt[:40]}{'...' if len(prompt) > 40 else ''}")
            print(f"    Time: {prompt_stats['avg_time']:.2f}s | "
                  f"Speed: {prompt_stats['avg_tokens_per_second']:.1f} tok/s | "
                  f"Consistency: {prompt_stats['consistency']:.2f}")
        
        print(f"\n{'='*80}")
    
    def save_results(self, filename: str = None):
        """Save results to JSON file"""
        if not filename:
            timestamp = int(time.time())
            filename = f"generation_speed_test_{self.model.replace(':', '_')}_{timestamp}.json"
        
        data = {
            "model": self.model,
            "timestamp": time.time(),
            "results": [
                {
                    "prompt": r.prompt,
                    "response_length": r.response_length,
                    "generation_time": r.generation_time,
                    "tokens_per_second": r.tokens_per_second,
                    "first_token_time": r.first_token_time,
                    "timestamp": r.timestamp
                }
                for r in self.results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Main function to run the speed test"""
    print("🧪 Generation Speed Tester")
    print("=" * 50)
    
    # Get model choice
    model_choice = input("Enter model name (default: qwen3:8b): ").strip()
    model = model_choice if model_choice else 'qwen3:8b'
    
    # Get test configuration
    try:
        iterations = int(input("Number of iterations per prompt (default: 3): ") or "3")
    except ValueError:
        iterations = 3
    
    # Create tester and run tests
    tester = GenerationSpeedTester(model)
    
    try:
        analysis = tester.run_comprehensive_test(iterations)
        tester.print_summary(analysis)
        
        # Ask if user wants to save results
        save_choice = input("\nSave results to file? (y/N): ").strip().lower()
        if save_choice in ['y', 'yes']:
            tester.save_results()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        if tester.results:
            print("Analyzing partial results...")
            analysis = tester.analyze_results(tester.results)
            tester.print_summary(analysis)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        raise

if __name__ == "__main__":
    main()