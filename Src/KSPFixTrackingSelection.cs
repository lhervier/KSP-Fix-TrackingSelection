using System;
using System.Reflection;
using HarmonyLib;
using UnityEngine;

namespace com.github.lhervier.ksp.fix.trackingselection
{
    /// <summary>
    /// Installs the fixes the settings turn on, once, when KSP starts: from then on, the tracking station's list
    /// no longer lights its top row with nothing selected, and a vessel the filters hide is no longer selected.
    /// </summary>
    [KSPAddon(KSPAddon.Startup.Instantly, true)]
    public class KSPFixTrackingSelection : MonoBehaviour
    {
        private const string HarmonyId = "com.github.lhervier.ksp.fix.trackingselection";

        private void Start()
        {
            Settings.Load();
            string version = typeof(KSPFixTrackingSelection).Assembly
                .GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion;
            Log.Info($"Version {version}, " +
                $"releaseRemovedRows {Settings.ReleaseRemovedRows}, deselectHiddenVessel {Settings.DeselectHiddenVessel}, " +
                $"log level {Log.Level}");
            Harmony harmony = new Harmony(HarmonyId);
            if (Settings.ReleaseRemovedRows)
            {
                try
                {
                    RemovedRows.Install(harmony);
                    Log.Info("Removed rows fix installed");
                }
                catch (Exception e)
                {
                    Log.Error($"Could not install the removed rows fix, the list lights its top row as on stock: {e}");
                }
            }
            if (Settings.DeselectHiddenVessel)
            {
                try
                {
                    HiddenSelection.Install(harmony);
                    Log.Info("Hidden selection fix installed");
                }
                catch (Exception e)
                {
                    Log.Error($"Could not install the hidden selection fix, a hidden vessel stays selected as on stock: {e}");
                }
            }
        }
    }
}
