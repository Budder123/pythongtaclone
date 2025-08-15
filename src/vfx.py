import os
from panda3d.core import Filename, Point3, Vec3, Vec4
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from direct.particles.ForceGroup import ForceGroup

def _configure_boost_effect(p):
    """Configures a Particles object for the boost effect."""
    p.setPoolSize(64)
    p.setBirthRate(0.01)
    p.setLitterSize(2)
    p.setLitterSpread(0)

    # Factory, Renderer, and Emitter setup
    p.factory.setLifespanBase(0.4)
    p.factory.setLifespanSpread(0.1)
    p.factory.setMassBase(1.0)
    p.factory.setMassSpread(0.0)
    p.factory.setTerminalVelocityBase(400.0)
    p.factory.setTerminalVelocitySpread(0.0)

    p.renderer.setAlphaMode(p.renderer.PRALPHAINOUT)
    p.renderer.setUserAlpha(0.6)
    p.renderer.setColor(Vec4(0.2, 0.4, 1.0, 1.0))
    p.renderer.setXScaleFlag(1)
    p.renderer.setYScaleFlag(1)
    p.renderer.setZScaleFlag(1)
    p.renderer.setInitialXScale(0.1)
    p.renderer.setFinalXScale(0.01)
    p.renderer.setInitialYScale(0.1)
    p.renderer.setFinalYScale(0.01)

    p.emitter.setEmissionType(p.emitter.ETRADIATE)
    p.emitter.setAmplitude(1.0)
    p.emitter.setAmplitudeSpread(0.0)
    p.emitter.setOffsetForce(Vec3(0.0, -5.0, 0.0))
    p.emitter.setExplicitLaunchVector(Vec3(1.0, 0.0, 0.0))
    p.emitter.setRadiateOrigin(Point3(0, 0, 0))

def _configure_sparks_effect(p):
    """Configures a Particles object for the sparks effect."""
    p.setPoolSize(128)
    p.setBirthRate(0.01)
    p.setLitterSize(20)
    p.setLitterSpread(0)

    p.emitter.setDuration(0.1)

    p.factory.setLifespanBase(0.5)
    p.factory.setLifespanSpread(0.2)
    p.factory.setMassBase(1.0)
    p.factory.setMassSpread(0.2)
    p.factory.setTerminalVelocityBase(400.0)
    p.factory.setTerminalVelocitySpread(0.0)

    p.renderer.setAlphaMode(p.renderer.PRALPHAINOUT)
    p.renderer.setUserAlpha(1.0)
    p.renderer.setColor(Vec4(1.0, 0.9, 0.5, 1.0))
    p.renderer.setXScaleFlag(1)
    p.renderer.setYScaleFlag(1)
    p.renderer.setZScaleFlag(1)
    p.renderer.setInitialXScale(0.1)
    p.renderer.setFinalXScale(0.0)
    p.renderer.setInitialYScale(0.02)
    p.renderer.setFinalYScale(0.0)

    p.emitter.setEmissionType(p.emitter.ETRADIATE)
    p.emitter.setAmplitude(8.0)
    p.emitter.setAmplitudeSpread(2.0)
    p.emitter.setRadiateOrigin(Point3(0, 0, 0))

    gravity_force = Vec3(0.0, 0.0, -15.0)
    force_group = ForceGroup()
    force_group.addForce(gravity_force)
    p.addForceGroup(force_group)

def create_boost_effect(base):
    """Creates a particle effect for the car's boost."""
    effect = ParticleEffect()
    particles = Particles('boost-particles')
    # We must enable the particle manager before starting particles
    base.enableParticles()
    _configure_boost_effect(particles)
    effect.addParticles(particles)
    return effect

def create_sparks_effect(base):
    """Creates a one-shot particle effect for collision sparks."""
    effect = ParticleEffect()
    particles = Particles('sparks-particles')
    # We must enable the particle manager before starting particles
    base.enableParticles()
    _configure_sparks_effect(particles)
    effect.addParticles(particles)
    return effect
