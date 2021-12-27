from client import ParticleClient

# Šis ir lietotāja norādītais fails
pc = ParticleClient("/home/marisn/tmp/rm_particle.py")
# Palaižam klientu ciklā. Kad cikls ir cauri, simulācija ir beigusies.
pc.run()
