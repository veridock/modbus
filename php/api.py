#!/usr/bin/env python
"""
Modbus RTU IO 8CH FastAPI Server
Provides HTTP API for controlling Waveshare Modbus RTU IO 8CH device
Uses mod.py ModbusRTUClient for actual hardware communication
"""

import asyncio
import time
import logging
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import the working ModbusRTUClient from mod.py
from mod import ModbusRTUClient, auto_detect_modbus_port

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
MODBUS_DEVICE_ADDRESS = int(os.getenv('MODBUS_DEVICE_ADDRESS', '1'))
UPDATE_INTERVAL = float(os.getenv('UPDATE_INTERVAL', '1.0'))

# FastAPI app
app = FastAPI(
    title="Modbus RTU IO 8CH API",
    description="REST API for Waveshare Modbus RTU IO 8CH control",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global modbus client
modbus_client: Optional[ModbusRTUClient] = None

# Pydantic models
class ControlRequest(BaseModel):
    channel: int
    action: str  # "on", "off", "toggle"

class ControlAllRequest(BaseModel):
    states: List[bool]  # Array of 8 boolean values

class StatusResponse(BaseModel):
    connected: bool
    outputs: List[bool]
    inputs: List[bool]
    timestamp: float

# Device state management using mod.py ModbusRTUClient
class DeviceState:
    def __init__(self):
        self.connected = False
        self.outputs = [False] * 8
        self.inputs = [False] * 8
        self.last_update = 0

# Global device state
device_state = DeviceState()

async def initialize_modbus_client():
    """Initialize the Modbus client using mod.py"""
    global modbus_client
    
    try:
        # Try auto-detection first
        port = auto_detect_modbus_port()
        if port:
            logger.info(f"Auto-detected Modbus device on port: {port}")
            modbus_client = ModbusRTUClient(port=port)
        else:
            # Fallback to .env configuration
            logger.info("Using .env configuration for Modbus connection")
            modbus_client = ModbusRTUClient()
        
        # Test connection
        if modbus_client.connect():
            device_state.connected = True
            logger.info("Successfully connected to Modbus device")
            
            # Initial state read
            await update_device_state()
        else:
            device_state.connected = False
            logger.error("Failed to connect to Modbus device")
            
    except Exception as e:
        logger.error(f"Error initializing Modbus client: {e}")
        device_state.connected = False

async def update_device_state():
    """Update device state by reading from hardware"""
    global modbus_client
    
    if not modbus_client or not device_state.connected:
        return
        
    try:
        # Read outputs (coils)
        outputs = modbus_client.read_coils(0, 8, unit=MODBUS_DEVICE_ADDRESS)
        if outputs is not None:
            device_state.outputs = outputs
            
        # Read inputs (discrete inputs)
        inputs = modbus_client.read_discrete_inputs(0, 8, unit=MODBUS_DEVICE_ADDRESS)
        if inputs is not None:
            device_state.inputs = inputs
            
        device_state.last_update = time.time()
        
    except Exception as e:
        logger.error(f"Error updating device state: {e}")
        device_state.connected = False

def write_single_output(channel: int, state: bool) -> bool:
    """Write single output channel using mod.py client"""
    global modbus_client
    
    if not modbus_client or not device_state.connected:
        logger.error("Modbus client not connected")
        return False
        
    try:
        if channel < 0 or channel > 7:
            logger.error(f"Invalid channel: {channel}")
            return False
            
        # Use mod.py client to write coil
        success = modbus_client.write_coil(channel, state, unit=MODBUS_DEVICE_ADDRESS)
        
        if success:
            device_state.outputs[channel] = state
            logger.info(f"Set output channel {channel} to {'ON' if state else 'OFF'}")
            return True
        else:
            logger.error(f"Failed to write output channel {channel}")
            return False
            
    except Exception as e:
        logger.error(f"Error writing single output: {e}")
        return False

async def background_update_task():
    """Background task to periodically update device state"""
    while True:
        try:
            await update_device_state()
            await asyncio.sleep(UPDATE_INTERVAL)
        except Exception as e:
            logger.error(f"Background update error: {e}")
            await asyncio.sleep(UPDATE_INTERVAL)  # Update every 500ms

@app.on_event("startup")
async def startup_event():
    """Initialize device connection on startup"""
    logger.info("Starting Modbus RTU IO 8CH API server...")
    await initialize_modbus_client()
    
    # Start background task for status updates
    asyncio.create_task(background_update_task())

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    global modbus_client
    if modbus_client:
        modbus_client.disconnect()
    logger.info("Modbus RTU IO 8CH API server shutdown")

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current device status"""
    return StatusResponse(
        connected=device_state.connected,
        outputs=device_state.outputs,
        inputs=device_state.inputs,
        timestamp=time.time()
    )

@app.post("/control")
async def control_output(request: ControlRequest):
    """Control digital output channel"""
    try:
        if not device_state.connected:
            raise HTTPException(status_code=503, detail="Device not connected")
            
        if request.channel < 0 or request.channel > 7:
            raise HTTPException(status_code=400, detail="Channel must be 0-7")
            
        current_state = device_state.outputs[request.channel]
        
        if request.action == "on":
            new_state = True
        elif request.action == "off":
            new_state = False
        elif request.action == "toggle":
            new_state = not current_state
        else:
            raise HTTPException(status_code=400, detail="Action must be 'on', 'off', or 'toggle'")
            
        if write_single_output(request.channel, new_state):
            return {
                "success": True,
                "channel": request.channel,
                "action": request.action,
                "new_state": new_state,
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to control output")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in control_output: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/control/all")
async def control_all_outputs(request: ControlAllRequest):
    """Control all digital output channels"""
    try:
        if not device_state.connected:
            raise HTTPException(status_code=503, detail="Device not connected")
            
        if len(request.states) != 8:
            raise HTTPException(status_code=400, detail="Must provide exactly 8 boolean values")
            
        success_count = 0
        for channel, state in enumerate(request.states):
            if write_single_output(channel, state):
                success_count += 1
            
        if success_count == 8:
            return {
                "success": True,
                "states": request.states,
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=500, detail=f"Only {success_count}/8 outputs controlled successfully")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in control_all_outputs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/device/info")
async def get_device_info():
    """Get device information"""
    return {
        "device": "Waveshare Modbus RTU IO 8CH",
        "status": "online" if device_state.connected else "offline",
        "last_update": device_state.last_update,
        "channels": {"inputs": 8, "outputs": 8}
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Modbus RTU IO 8CH API",
        "status": "running",
        "connected": device_state.connected
    }

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8090,
        reload=False,
        log_level="info"
    )
