using HarmonyLib;
using KSP.UI.Screens;
using UnityEngine;

namespace com.github.lhervier.ksp.fix.trackingselection
{
    /// <summary>
    /// Deselects the tracking station's selected vessel when the vessel type filters hide it, as the station's list
    /// is rebuilt, so that Fly, Recover and Terminate can no longer act on a vessel the list does not show.
    ///
    /// On stock, a filter that hides the selected vessel leaves it selected: its row is gone, the buttons still act
    /// on it, and another row may look selected instead.
    /// </summary>
    internal static class HiddenSelection
    {
        // Private in SpaceTracking: the frame SetVessel last ran in. SetVessel does nothing when called twice in
        // the same frame.
        private static readonly AccessTools.FieldRef<SpaceTracking, int> LastSetVesselFrame =
            AccessTools.FieldRefAccess<SpaceTracking, int>("lastSetVesselFrame");

        /// <summary>Patches SpaceTracking.ConstructUIList with <see cref="Prefix"/>.</summary>
        public static void Install(Harmony harmony)
        {
            var target = AccessTools.Method(typeof(SpaceTracking), "ConstructUIList");
            harmony.Patch(target, prefix: new HarmonyMethod(typeof(HiddenSelection), nameof(Prefix)));
        }

        /// <summary>
        /// Deselects the selected vessel of <paramref name="__instance"/> when the filters hide it, before the
        /// list is rebuilt without it.
        /// </summary>
        private static void Prefix(SpaceTracking __instance)
        {
            Vessel selected = __instance.SelectedVessel;
            if (selected == null || MapViewFiltering.CheckAgainstFilter(selected))
            {
                return;
            }
            // A vessel selected earlier in this frame would make SetVessel ignore the deselection.
            if (LastSetVesselFrame(__instance) == Time.frameCount)
            {
                LastSetVesselFrame(__instance) = Time.frameCount - 1;
            }
            string name = selected.GetDisplayName();
            // As End Track does for a vessel that leaves the list but stays in the game: the camera keeps its target.
            __instance.SetVessel(null, true);
            Log.Debug($"{name} is selected but the filters hide it: deselected");
        }
    }
}
