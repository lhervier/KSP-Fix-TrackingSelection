using HarmonyLib;
using KSP.UI.Screens;
using UnityEngine.UI;

namespace com.github.lhervier.ksp.fix.trackingselection
{
    /// <summary>
    /// Takes each row the tracking station removes from its list out of the list's toggle group at once, so that
    /// the row's destruction no longer lights the top row of the new list.
    ///
    /// The rows of the list are toggles of one group that never lets them all go off. When the station rebuilds
    /// the list (a vessel terminated or recovered, a filter changed...), it unregisters the old rows from the group
    /// and destroys them, but each keeps the group as its own. Unity destroys them at the end of the frame, and a
    /// toggle being destroyed makes its group check that one toggle is on: when none is, as when no vessel of the
    /// new list is selected, the group switches on the first one. The top row then shows as selected while no
    /// vessel is, and a click on it does nothing, since it is on already.
    /// </summary>
    internal static class RemovedRows
    {
        /// <summary>Patches TrackingStationWidget.Terminate with <see cref="Postfix"/>.</summary>
        public static void Install(Harmony harmony)
        {
            var target = AccessTools.Method(typeof(TrackingStationWidget), nameof(TrackingStationWidget.Terminate));
            harmony.Patch(target, postfix: new HarmonyMethod(typeof(RemovedRows), nameof(Postfix)));
        }

        /// <summary>Takes the toggle of <paramref name="__instance"/>, a row being removed, out of its group.</summary>
        private static void Postfix(TrackingStationWidget __instance)
        {
            Toggle toggle = __instance.toggle;
            if (toggle == null || toggle.group == null)
            {
                return;
            }
            // Setting the group to null unregisters the toggle again, which does nothing, and forgets the group:
            // Toggle.OnDestroy then has no group to check.
            toggle.group = null;
            if (Log.IsDebugEnabled)
            {
                // A vessel terminated or recovered is gone from the game before its row is removed.
                string name = __instance.vessel != null ? __instance.vessel.GetDisplayName() : "a vessel no longer in the game";
                Log.Debug($"Row of {name} removed from the list, out of its toggle group");
            }
        }
    }
}
