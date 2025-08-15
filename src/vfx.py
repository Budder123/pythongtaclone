import os
from panda3d.core import Filename, Point3, Vec3, Vec4
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from direct.particles.ForceGroup import ForceGroup

def create_boost_effect(base):
    """Creates a particle effect for the car's boost."""
    p = ParticleEffect()
    p.reparentTo(base.render) # Will be reparented to the car later

    # Particles parameters
    p.particles.setPoolSize(64)
    p.particles.setBirthRate(0.01)
    p.particles.setLitterSize(2)
    p.particles.setLitterSpread(0)

    # Factory parameters
    p.factory.setLifespanBase(0.4)
    p.factory.setLifespanSpread(0.1)
    p.factory.setMassBase(1.0)
    p.factory.setMassSpread(0.0)
    p.factory.setTerminalVelocityBase(400.0)
    p.factory.setTerminalVelocitySpread(0.0)

    # Renderer parameters
    p.renderer.setAlphaMode(p.renderer.PRALPHAINOUT)
    p.renderer.setUserAlpha(0.6)
    p.renderer.setFromNode(None) # Use a texture instead of a model
    p.renderer.setColor(Vec4(0.2, 0.4, 1.0, 1.0))
    p.renderer.setXScaleFlag(1)
    p.renderer.setYScaleFlag(1)
    p.renderer.setZScaleFlag(1)
    p.renderer.setInitialXScale(0.1)
    p.renderer.setFinalXScale(0.01)
    p.renderer.setInitialYScale(0.1)
    p.renderer.setFinalYScale(0.01)

    # Emitter parameters
    p.emitter.setEmissionType(p.emitter.ETRADIATE)
    p.emitter.setAmplitude(1.0)
    p.emitter.setAmplitudeSpread(0.0)
    p.emitter.setOffsetForce(Vec3(0.0, -5.0, 0.0))
    p.emitter.setExplicitLaunchVector(Vec3(1.0, 0.0, 0.0))
    p.emitter.setRadiateOrigin(Point3(0, 0, 0))

    return p

def create_sparks_effect(base):
    """Creates a one-shot particle effect for collision sparks."""
    p = ParticleEffect()
    p.reparentTo(base.render)
    p.setPos(0, 0, 0)

    # Set up a one-shot burst
    p.particles.setPoolSize(128)
    p.particles.setBirthRate(0.01)
    p.particles.setLitterSize(20)
    p.particles.setLitterSpread(0)
    p.emitter.setDuration(0.1) # Emit for a short time

    # Factory parameters
    p.factory.setLifespanBase(0.5)
    p.factory.setLifespanSpread(0.2)
    p.factory.setMassBase(1.0)
    p.factory.setMassSpread(0.2)
    p.factory.setTerminalVelocityBase(400.0)
    p.factory.setTerminalVelocitySpread(0.0)

    # Renderer parameters
    p.renderer.setAlphaMode(p.renderer.PRALPHAINOUT)
    p.renderer.setUserAlpha(1.0)
    p.renderer.setFromNode(None)
    p.renderer.setColor(Vec4(1.0, 0.9, 0.5, 1.0)) # Bright yellow/white
    p.renderer.setXScaleFlag(1)
    p.renderer.setYScaleFlag(1)
    p.renderer.setZScaleFlag(1)
    p.renderer.setInitialXScale(0.1)
    p.renderer.setFinalXScale(0.0)
    p.renderer.setInitialYScale(0.02)
    p.renderer.setFinalYScale(0.0)

    # Emitter parameters
    p.emitter.setEmissionType(p.emitter.ETRADIATE)
    p.emitter.setAmplitude(8.0)
    p.emitter.setAmplitudeSpread(2.0)
    p.emitter.setRadiateOrigin(Point3(0, 0, 0))

    # Add a gravity force
    gravity_force = Vec3(0.0, 0.0, -15.0)
    force_group = ForceGroup()
    force_group.addForce(gravity_force)
    p.addForceGroup(force_group)

    return p
