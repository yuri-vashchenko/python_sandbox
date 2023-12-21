# FIND DEVICE

import asyncio
from bleak import BleakScanner
from bleak import BleakClient
import logging

logger = logging.getLogger(__name__)
log_level = logging.INFO
logging.basicConfig(
    level=log_level,
    format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
)

async def discover(name):
    logger.info(f"Running BLE discover for {name} devices")
    found = []
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name:
            if d.name.lower().startswith(name.lower()):
                found.append(d)
    return found

async def connect(address):
    logger.info(f"Connecting to device {address}...")
    async with BleakClient(address) as client:
        logger.info("Getting client services...")
        for service in client.services:
            logger.info("[Service] %s", service)

            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value = await client.read_gatt_char(char.uuid)
                        logger.info(
                            "  [Characteristic] %s (%s), Value: %r",
                            char,
                            ",".join(char.properties),
                            value,
                        )
                    except Exception as e:
                        logger.error(
                            "  [Characteristic] %s (%s), Error: %s",
                            char,
                            ",".join(char.properties),
                            e,
                        )

                else:
                    logger.info(
                        "  [Characteristic] %s (%s)", char, ",".join(char.properties)
                    )

                for descriptor in char.descriptors:
                    try:
                        value = await client.read_gatt_descriptor(descriptor.handle)
                        logger.info("    [Descriptor] %s, Value: %r", descriptor, value)
                    except Exception as e:
                        logger.error("    [Descriptor] %s, Error: %s", descriptor, e)

        logger.info("disconnecting...")

    logger.info("disconnected")

nanits = asyncio.run(discover("nanit"))

logger.info(f"Found {len(nanits)} nanit device(s)")
if len(nanits) > 0:
    (address, name) = nanits[0].address, nanits[0].name
    asyncio.run(connect(address))

