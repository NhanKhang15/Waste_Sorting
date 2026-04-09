const SocialButton: React.FC<{ icon: string, text: string}> = ({ icon, text }) => {
    return (
        <button className="w-full py-4 bg-surface-container-lowest border border-outline rounded-full flex items-center justify-center gap-3 hover:bg-surface-container-Low transition-all">
            <span className="material-symbols-ounlined text-xl">
                {icon}
            </span>
            <span className="text-on-surface-variant font-medium">
                {text}
            </span>
        </button>
    )
}
    

export default SocialButton;