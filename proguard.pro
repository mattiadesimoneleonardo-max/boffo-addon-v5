# Obfuscation only, kein Shrink/Optimize (sonst bricht Meteor/Fabric)
-dontshrink
-dontoptimize
-dontnotes
-dontwarn **
-ignorewarnings
-useuniqueclassmembernames
-adaptresourcefilecontents fabric.mod.json
-keepattributes *Annotation*,Signature,InnerClasses,EnclosingMethod,RuntimeVisibleAnnotations

# Fabric/Meteor Entrypoint
-keep class com.boffo.addon.** { *; }
-keep class * extends meteordevelopment.meteorclient.MeteorAddon { *; }

# Meteor-Module, Commands, HUD-Elemente: Namen + Methoden behalten (Meteor findet sie per Reflection)
-keep class * extends meteordevelopment.meteorclient.systems.modules.Module { public protected *; }
-keep class * extends meteordevelopment.meteorclient.commands.Command { public protected *; }
-keep class * extends meteordevelopment.meteorclient.systems.hud.HudElement { public protected *; }

# Orbit Event-Bus (@EventHandler) und Mixins
-keepclassmembers class * { @meteordevelopment.orbit.EventHandler *; }
-keep @org.spongepowered.asm.mixin.Mixin class * { *; }

# Ressourcen / Package-Namen nicht umbauen
-keeppackagenames
