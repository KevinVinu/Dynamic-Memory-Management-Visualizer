import streamlit as st
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import seaborn as sns
from collections import deque, OrderedDict

# Set page configuration
st.set_page_config(page_title="Memory Management Visualizer", layout="wide")

def main():
    st.title("Dynamic Memory Management Visualizer")
    st.sidebar.header("Settings")
    
    technique = st.sidebar.selectbox(
        "Memory Management Technique",
        ["Paging", "Segmentation", "Virtual Memory"]
    )

    if technique == "Paging":
        paging_simulator()
    elif technique == "Segmentation":
        segmentation_simulator()
    else:
        virtual_memory_simulator()

def paging_simulator():
    st.header("Paging Simulation")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Parameters")
        page_size = st.number_input("Page Size (KB)", min_value=1, value=4, step=1)
        physical_memory = st.number_input("Physical Memory Size (KB)", min_value=page_size, value=32, step=4)
        
        # Calculate the number of frames
        num_frames = physical_memory // page_size
        st.info(f"Number of frames: {num_frames}")
        
        # Input for the page reference string
        reference_input = st.text_area("Enter page reference sequence (comma-separated)", "1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5")
        
        try:
            page_references = [int(x.strip()) for x in reference_input.split(",")]
        except ValueError:
            st.error("Please enter valid numbers separated by commas")
            return
            
        algo = st.selectbox("Page Replacement Algorithm", ["FIFO", "LRU", "Optimal"])
        
        if st.button("Run Simulation"):
            frames, page_faults = simulate_paging(page_references, num_frames, algo)
            with col2:
                st.subheader("Simulation Results")
                display_paging_results(frames, page_references, page_faults, algo)

def simulate_paging(page_references, num_frames, algorithm):
    frames = []
    page_faults = []
    
    if algorithm == "FIFO":
        queue = deque(maxlen=num_frames)
        for page in page_references:
            if page not in queue:
                page_faults.append(True)
                if len(queue) == num_frames:
                    queue.popleft()  # Remove the oldest page
                queue.append(page)
            else:
                page_faults.append(False)
            frame_state = list(queue)
            # Pad with None if not full
            while len(frame_state) < num_frames:
                frame_state.append(None)
            frames.append(frame_state.copy())
    
    elif algorithm == "LRU":
        lru_dict = OrderedDict()
        for page in page_references:
            if page not in lru_dict:
                page_faults.append(True)
                if len(lru_dict) == num_frames:
                    lru_dict.popitem(last=False)  # Remove least recently used
                lru_dict[page] = True
            else:
                page_faults.append(False)
                # Move to the end (most recently used)
                lru_dict.move_to_end(page)
            frame_state = list(lru_dict.keys())
            # Pad with None if not full
            while len(frame_state) < num_frames:
                frame_state.append(None)
            frames.append(frame_state.copy())
    
    elif algorithm == "Optimal":
        frame_state = [None] * num_frames
        for i, page in enumerate(page_references):
            if page not in frame_state:
                page_faults.append(True)
                if None in frame_state:
                    # Fill empty slot
                    frame_state[frame_state.index(None)] = page
                else:
                    # Find the page that won't be used for the longest time
                    future_indices = {}
                    for j, p in enumerate(frame_state):
                        try:
                            next_use = page_references[i+1:].index(p)
                            future_indices[j] = next_use
                        except ValueError:
                            # Page not used in the future
                            future_indices[j] = float('inf')
                    
                    if future_indices:
                        # Replace the page with the furthest next use
                        to_replace = max(future_indices, key=future_indices.get)
                        frame_state[to_replace] = page
            else:
                page_faults.append(False)
            
            frames.append(frame_state.copy())
            
    return frames, page_faults

def display_paging_results(frames, page_references, page_faults, algorithm):
    # Create a detailed page table visualization showing frame state and faults
    st.subheader("Page Table Visualization")
    
    # Create a dataframe for the page table visualization
    page_table_data = []
    
    for i, (frame_state, page_ref, fault) in enumerate(zip(frames, page_references, page_faults)):
        row = {
            "Reference #": i + 1,
            "Page Referenced": page_ref,
            "Status": "Page Fault" if fault else "Page Hit"
        }
        
        # Add frame contents for each access
        for j, page in enumerate(frame_state):
            row[f"Frame {j+1}"] = page if page is not None else "-"
            
        # Highlight which frame contains the requested page
        # (or will after the page fault is handled)
        if page_ref in frame_state:
            frame_index = frame_state.index(page_ref)
            row["In Frame"] = frame_index + 1
        else:
            row["In Frame"] = "-" 
            
        page_table_data.append(row)
    
    # Create and display the DataFrame
    page_table_df = pd.DataFrame(page_table_data)
    
    # Style the dataframe to highlight page faults in red and page hits in green
    def highlight_faults(row):
        if row['Status'] == 'Page Fault':
            return ['background-color: #000000'] * len(row)
        elif row['Status'] == 'Page Hit':
            return ['background-color: #000000'] * len(row)
        return [''] * len(row)
    
    # Display the styled dataframe
    st.dataframe(page_table_df.style.apply(highlight_faults, axis=1))
    
    # Calculate and display metrics
    total_accesses = len(page_references)
    total_faults = sum(page_faults)
    fault_rate = (total_faults / total_accesses) * 100
    hit_rate = 100 - fault_rate
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Accesses", total_accesses)
    with col2:
        st.metric("Total Page Faults", total_faults)
    with col3:
        st.metric("Page Fault Rate", f"{fault_rate:.2f}%")
    with col4:
        st.metric("Page Hit Rate", f"{hit_rate:.2f}%")
    
    # Summary statistics
    st.subheader("Summary of Page Table")
    
    # Display frame contents at the end of simulation
    final_frame_state = frames[-1]
    
    st.write("Final Memory State:")
    final_state = {}
    for i, page in enumerate(final_frame_state):
        final_state[f"Frame {i+1}"] = page if page is not None else "Empty"
    
    st.table(pd.DataFrame([final_state]))
    
    # Create a visualization of page fault/hit pattern
    st.subheader("Page Fault/Hit Pattern")
    
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.bar(range(len(page_faults)), 
           [1 if fault else 0.5 for fault in page_faults], 
           color=['red' if fault else 'green' for fault in page_faults])
    
    # Add labels to each bar
    for i, (fault, page) in enumerate(zip(page_faults, page_references)):
        label = "Fault" if fault else "Hit"
        ax.text(i, 1.1 if fault else 0.6, f"P{page}\n({label})", 
                ha='center', va='center', fontsize=9)
    
    ax.set_ylim(0, 1.5)
    ax.set_yticks([0.25, 0.75])
    ax.set_yticklabels(['Hit', 'Fault'])
    ax.set_xlabel("Access Sequence")
    ax.set_title(f"Page Fault/Hit Pattern with {algorithm} Algorithm")
    
    # Remove x-ticks for cleaner look
    ax.set_xticks([])
    
    st.pyplot(fig)

def segmentation_simulator():
    st.header("Segmentation Simulation")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Parameters")
        memory_size = st.number_input("Total Memory Size", min_value=10, value=100, step=10)
        
        segment_sizes = []
        segment_count = st.number_input("Number of Segments", min_value=1, value=3, step=1, max_value=10)
        
        for i in range(segment_count):
            size = st.number_input(f"Segment {i+1} Size", min_value=1, value=10, key=f"seg_{i}")
            segment_sizes.append(size)
        
        allocation_method = st.selectbox("Allocation Method", ["First Fit", "Best Fit", "Worst Fit"])
        
        if st.button("Run Simulation"):
            with col2:
                st.subheader("Simulation Results")
                display_segmentation_results(memory_size, segment_sizes, allocation_method)

def display_segmentation_results(memory_size, segment_sizes, allocation_method):
    # Initialize memory as one free block
    memory = [(0, memory_size, None)]  # (start, size, segment_id or None for free)
    
    segment_allocations = []
    
    for i, size in enumerate(segment_sizes):
        segment_id = i + 1
        allocation = allocate_segment(memory, size, segment_id, allocation_method)
        
        if allocation:
            segment_allocations.append((segment_id, allocation[0], allocation[1]))
        else:
            st.error(f"Could not allocate Segment {segment_id} (size {size})")
    
    # Visualization of memory state
    fig, ax = plt.subplots(figsize=(10, 6))
    y_pos = 0
    
    # Plot memory blocks
    for start, size, segment_id in memory:
        if segment_id is None:
            color = 'lightgray'
            label = 'Free'
        else:
            color = plt.cm.tab10(segment_id % 10)
            label = f'Segment {segment_id}'
        
        ax.barh(y_pos, size, left=start, height=0.5, color=color, edgecolor='black')
        ax.text(start + size/2, y_pos, f"{label} ({size})", ha='center', va='center')
    
    ax.set_xlim(0, memory_size)
    ax.set_yticks([])
    ax.set_xlabel('Memory Address')
    ax.set_title(f'Memory Segmentation ({allocation_method})')
    
    st.pyplot(fig)
    
    # Display segment table
    st.subheader("Segment Table")
    segment_table = []
    for segment_id, start, size in segment_allocations:
        segment_table.append({
            "Segment": segment_id,
            "Base Address": start,
            "Size": size,
            "Limit": start + size - 1
        })
    
    st.table(pd.DataFrame(segment_table))
    
    # Memory utilization
    allocated_memory = sum(size for _, _, size in segment_allocations)
    utilization = (allocated_memory / memory_size) * 100
    fragmentation = sum(size for start, size, segment_id in memory if segment_id is None)
    
    st.metric("Memory Utilization", f"{utilization:.2f}%")
    st.metric("External Fragmentation", fragmentation)

def allocate_segment(memory, size, segment_id, method):
    free_blocks = [(start, block_size) for start, block_size, id in memory if id is None and block_size >= size]
    
    if not free_blocks:
        return None
    
    if method == "First Fit":
        start, block_size = free_blocks[0]
    elif method == "Best Fit":
        start, block_size = min(free_blocks, key=lambda x: x[1])
    else:  # Worst Fit
        start, block_size = max(free_blocks, key=lambda x: x[1])
    
    # Find the index of the free block in memory
    for i, (block_start, block_size, block_id) in enumerate(memory):
        if block_start == start and block_id is None:
            # Remove the free block
            memory.pop(i)
            
            # Add the allocated block
            memory.insert(i, (start, size, segment_id))
            
            # If there's remaining space, add a new free block
            if block_size > size:
                memory.insert(i + 1, (start + size, block_size - size, None))
            
            # Sort memory blocks by start address
            memory.sort(key=lambda x: x[0])
            
            return (start, size)
    
    return None

def virtual_memory_simulator():
    st.header("Virtual Memory Simulation")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Parameters")
        page_size = st.number_input("Page Size (KB)", min_value=1, value=4, step=1)
        physical_memory = st.number_input("Physical Memory Size (KB)", min_value=page_size, value=16, step=4)
        virtual_memory = st.number_input("Virtual Memory Size (KB)", min_value=physical_memory, value=64, step=4)
        
        # Calculate pages and frames
        num_pages = virtual_memory // page_size
        num_frames = physical_memory // page_size
        
        st.info(f"Virtual address space: {num_pages} pages")
        st.info(f"Physical address space: {num_frames} frames")
        
        # Generate virtual addresses
        address_count = st.number_input("Number of Memory Accesses", min_value=5, value=10, step=1)
        
        if st.button("Generate Random Memory Accesses"):
            # Generate random virtual addresses
            np.random.seed(42)  # For reproducibility
            addresses = np.random.randint(0, virtual_memory, size=address_count)
            access_sequence = [addr for addr in addresses]
            
            # Convert to page references
            page_references = [addr // page_size for addr in access_sequence]
            
            with col2:
                st.subheader("Memory Access Sequence")
                
                # Display the memory access details
                access_data = []
                for i, (addr, page) in enumerate(zip(access_sequence, page_references)):
                    access_data.append({
                        "Access #": i+1,
                        "Virtual Address": addr,
                        "Page Number": page,
                        "Offset": addr % page_size
                    })
                
                st.dataframe(pd.DataFrame(access_data))
                
                # Simulate page replacements
                st.subheader("Page Replacement Simulation")
                algo = st.selectbox("Page Replacement Algorithm", ["FIFO", "LRU"])
                
                # Run simulation
                frames, page_faults = simulate_virtual_memory(page_references, num_frames, algo)
                
                # Display the page table and frame mapping
                display_virtual_memory_results(frames, page_references, page_faults, access_sequence, num_pages, num_frames, algo, page_size)

def simulate_virtual_memory(page_references, num_frames, algorithm):
    frame_states = []
    page_faults = []
    
    # Initialize page table - all pages invalid initially
    page_table = {i: None for i in range(max(page_references) + 1)}
    frame_to_page = {i: None for i in range(num_frames)}
    
    if algorithm == "FIFO":
        queue = deque(maxlen=num_frames)
        for page in page_references:
            frame_state = frame_to_page.copy()
            
            if page_table[page] is None:  # Page fault
                page_faults.append(True)
                
                if len(queue) == num_frames and all(frame_to_page[f] is not None for f in range(num_frames)):  # Memory full, need replacement
                    old_frame = queue.popleft()
                    old_page = frame_to_page[old_frame]
                    
                    # Invalidate the old page
                    if old_page is not None:
                        page_table[old_page] = None
                    
                    # Assign the new page
                    frame_to_page[old_frame] = page
                    page_table[page] = old_frame
                    queue.append(old_frame)
                else:  # Find first free frame
                    free_frame = None
                    for frame, pg in frame_to_page.items():
                        if pg is None:
                            free_frame = frame
                            break
                    
                    frame_to_page[free_frame] = page
                    page_table[page] = free_frame
                    queue.append(free_frame)
            else:  # Page hit
                page_faults.append(False)
            
            frame_states.append(frame_to_page.copy())
    
    elif algorithm == "LRU":
        lru = {}  # Maps page to last access time
        for i, page in enumerate(page_references):
            frame_state = frame_to_page.copy()
            
            if page_table[page] is None:  # Page fault
                page_faults.append(True)
                
                if len([p for p in page_table.values() if p is not None]) == num_frames:  # Memory full
                    # Find least recently used page
                    least_recent_page = min(
                        [p for p in page_table if page_table[p] is not None],
                        key=lambda p: lru.get(p, -1)
                    )
                    
                    old_frame = page_table[least_recent_page]
                    page_table[least_recent_page] = None
                    
                    # Assign the new page
                    frame_to_page[old_frame] = page
                    page_table[page] = old_frame
                else:  # Find first free frame
                    free_frame = None
                    for frame, pg in frame_to_page.items():
                        if pg is None:
                            free_frame = frame
                            break
                    
                    frame_to_page[free_frame] = page
                    page_table[page] = free_frame
            else:  # Page hit
                page_faults.append(False)
            
            # Update access time for LRU
            lru[page] = i
            frame_states.append(frame_to_page.copy())
    
    return frame_states, page_faults

def display_virtual_memory_results(frames, page_references, page_faults, access_sequence, num_pages, num_frames, algorithm, page_size):
    # Create a comprehensive page table visualization
    st.subheader("Page Table Entries and Memory Access Results")
    
    page_table_data = []
    
    # Reverse the mapping from frames to page numbers
    for i, (frame_state, page_ref, virtual_addr, fault) in enumerate(
        zip(frames, page_references, access_sequence, page_faults)):
        
        # Get page-to-frame mapping
        page_to_frame = {page: frame for frame, page in frame_state.items() if page is not None}
        
        # Build the row data
        row = {
            "Access #": i + 1,
            "Virtual Address": virtual_addr,
            "Page #": page_ref,
            "Offset": virtual_addr % page_size,
            "Status": "Page Fault" if fault else "Page Hit",
        }
        
        # If page is in memory, calculate physical address
        if page_ref in page_to_frame:
            frame = page_to_frame[page_ref]
            physical_address = (frame * page_size) + (virtual_addr % page_size)
            row["Frame #"] = frame
            row["Physical Address"] = physical_address
            row["Valid Bit"] = "1"
        else:
            row["Frame #"] = "Not in memory"
            row["Physical Address"] = "N/A"
            row["Valid Bit"] = "0"
        
        # Add current memory state (which pages are in which frames)
        for f in range(num_frames):
            page_in_frame = frame_state.get(f)
            row[f"Frame {f} Contains"] = page_in_frame if page_in_frame is not None else "Empty"
            
        page_table_data.append(row)
    
    # Create and style the DataFrame for better visualization
    page_table_df = pd.DataFrame(page_table_data)
    
    # Style the dataframe to highlight page faults and hits
    def highlight_page_status(row):
        if row['Status'] == 'Page Fault':
            return ['background-color: #FFCCCB'] * len(row)  # Light red for faults
        else:
            return ['background-color: #CCFFCC'] * len(row)  # Light green for hits
    
    # Display the page table
    st.dataframe(page_table_df.style.apply(highlight_page_status, axis=1))
    
    # Calculate and display metrics
    total_accesses = len(page_references)
    total_faults = sum(page_faults)
    fault_rate = (total_faults / total_accesses) * 100
    hit_rate = 100 - fault_rate
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Accesses", total_accesses)
    with col2:
        st.metric("Total Page Faults", total_faults)
    with col3:
        st.metric("Page Fault Rate", f"{fault_rate:.2f}%")
    with col4:
        st.metric("Page Hit Rate", f"{hit_rate:.2f}%")
    
    # Display the final page table
    st.subheader("Final Page Table")
    
    # Create the final page table view
    final_frame_state = frames[-1]
    page_to_frame = {page: frame for frame, page in final_frame_state.items() if page is not None}
    
    final_page_table = []
    for page in range(num_pages):
        valid = page in page_to_frame
        entry = {
            "Page #": page,
            "Valid": "1" if valid else "0",
            "Frame #": page_to_frame.get(page, "N/A") if valid else "N/A",
            "Present": "Yes" if valid else "No"
        }
        final_page_table.append(entry)
    
    # Display final page table
    st.dataframe(pd.DataFrame(final_page_table))
    
    # Show the final physical memory state
    st.subheader("Final Physical Memory State")
    
    physical_memory = []
    for frame in range(num_frames):
        page = final_frame_state.get(frame)
        physical_memory.append({
            "Frame #": frame,
            "Contains Page": page if page is not None else "Empty",
            "Status": "Used" if page is not None else "Free"
        })
    
    st.dataframe(pd.DataFrame(physical_memory))

if __name__ == "__main__":
    main()